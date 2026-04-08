"""
Google Drive API client for fabric mock automation.
Handles listing, downloading, uploading, and organizing files in Drive.
"""

import io
import json
import os
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from .config import (
    DRIVE_INPUT_FOLDER_ID,
    DRIVE_OUTPUT_FOLDER_ID,
    GOOGLE_SERVICE_ACCOUNT_JSON,
    MOVE_PROCESSED_FILES,
    OUTPUT_FORMAT,
)

SCOPES = ["https://www.googleapis.com/auth/drive"]

_service = None


def get_service():
    """Return an authenticated Drive service (singleton)."""
    global _service
    if _service is not None:
        return _service

    info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    _service = build("drive", "v3", credentials=creds, cache_discovery=False)
    return _service


def list_input_images() -> list[dict]:
    """
    List all image files in the input folder.
    Returns list of dicts with keys: id, name, mimeType.
    """
    svc = get_service()
    image_mimes = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "image/bmp",
        "image/tiff",
    ]
    mime_query = " or ".join(f"mimeType='{m}'" for m in image_mimes)
    query = f"'{DRIVE_INPUT_FOLDER_ID}' in parents and ({mime_query}) and trashed=false"

    results = []
    page_token = None
    while True:
        resp = (
            svc.files()
            .list(
                q=query,
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token,
            )
            .execute()
        )
        results.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return results


def already_processed_names() -> set[str]:
    """
    Return a set of design base names that already have output subfolders
    in the output folder. Used to skip re-processing.
    """
    svc = get_service()
    query = (
        f"'{DRIVE_OUTPUT_FOLDER_ID}' in parents and "
        "mimeType='application/vnd.google-apps.folder' and trashed=false"
    )
    resp = (
        svc.files()
        .list(q=query, spaces="drive", fields="files(name)")
        .execute()
    )
    return {f["name"] for f in resp.get("files", [])}


def download_file_bytes(file_id: str) -> bytes:
    """Download a file from Drive by ID and return its bytes."""
    svc = get_service()
    request = svc.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue()


def get_or_create_output_subfolder(base_name: str) -> str:
    """
    Get the ID of the output subfolder named `base_name` inside the output
    folder, creating it if it doesn't exist.
    """
    svc = get_service()
    query = (
        f"'{DRIVE_OUTPUT_FOLDER_ID}' in parents and "
        f"name='{base_name}' and "
        "mimeType='application/vnd.google-apps.folder' and trashed=false"
    )
    resp = svc.files().list(q=query, spaces="drive", fields="files(id)").execute()
    files = resp.get("files", [])
    if files:
        return files[0]["id"]

    # Create the subfolder
    metadata = {
        "name": base_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [DRIVE_OUTPUT_FOLDER_ID],
    }
    folder = svc.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def upload_mock_image(
    image_bytes: bytes,
    filename: str,
    folder_id: str,
    mime_type: str = "image/jpeg",
) -> Optional[str]:
    """
    Upload mock image bytes to the given Drive folder.
    Returns the new file's Drive ID, or None on failure.
    """
    svc = get_service()
    metadata = {"name": filename, "parents": [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(image_bytes), mimetype=mime_type, resumable=False)
    try:
        file = (
            svc.files()
            .create(body=metadata, media_body=media, fields="id")
            .execute()
        )
        return file.get("id")
    except Exception as e:
        print(f"    [Drive] Upload failed for {filename}: {e}")
        return None


def move_to_processed(file_id: str, filename: str) -> None:
    """
    Move the input file to a 'Processed' subfolder inside the input folder,
    creating it if needed. Only runs if MOVE_PROCESSED_FILES is True.
    """
    if not MOVE_PROCESSED_FILES:
        return

    svc = get_service()

    # Find or create 'Processed' subfolder in input folder
    query = (
        f"'{DRIVE_INPUT_FOLDER_ID}' in parents and "
        "name='Processed' and "
        "mimeType='application/vnd.google-apps.folder' and trashed=false"
    )
    resp = svc.files().list(q=query, spaces="drive", fields="files(id)").execute()
    files = resp.get("files", [])
    if files:
        processed_id = files[0]["id"]
    else:
        metadata = {
            "name": "Processed",
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [DRIVE_INPUT_FOLDER_ID],
        }
        folder = svc.files().create(body=metadata, fields="id").execute()
        processed_id = folder["id"]

    # Move the file: add new parent, remove old parent
    svc.files().update(
        fileId=file_id,
        addParents=processed_id,
        removeParents=DRIVE_INPUT_FOLDER_ID,
        fields="id, parents",
    ).execute()
    print(f"    [Drive] Moved '{filename}' to Processed/")


def upload_log(csv_content: str, log_filename: str = "batch_log.csv") -> Optional[str]:
    """
    Upload (or overwrite) the CSV log file to the output folder root.
    Returns the file ID or None on failure.
    """
    svc = get_service()

    # Check if log file already exists (overwrite it)
    query = (
        f"'{DRIVE_OUTPUT_FOLDER_ID}' in parents and "
        f"name='{log_filename}' and trashed=false"
    )
    resp = svc.files().list(q=query, spaces="drive", fields="files(id)").execute()
    existing = resp.get("files", [])

    csv_bytes = csv_content.encode("utf-8")
    media = MediaIoBaseUpload(
        io.BytesIO(csv_bytes), mimetype="text/csv", resumable=False
    )

    try:
        if existing:
            file = (
                svc.files()
                .update(fileId=existing[0]["id"], media_body=media, fields="id")
                .execute()
            )
        else:
            metadata = {"name": log_filename, "parents": [DRIVE_OUTPUT_FOLDER_ID]}
            file = (
                svc.files()
                .create(body=metadata, media_body=media, fields="id")
                .execute()
            )
        return file.get("id")
    except Exception as e:
        print(f"    [Drive] Log upload failed: {e}")
        return None
