import io
import json
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive']

SUPPORTED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/webp',
    'image/heic', 'image/heif'
}


class DriveClient:
    def __init__(self, config):
        creds_info = json.loads(config.google_service_account_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_info, scopes=SCOPES
        )
        self.service = build('drive', 'v3', credentials=credentials)

    def list_image_files(self, folder_id):
        results = []
        page_token = None
        while True:
            response = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token
            ).execute()
            for f in response.get('files', []):
                if f['mimeType'] in SUPPORTED_MIME_TYPES:
                    results.append(f)
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        return results

    def list_subfolders(self, folder_id):
        response = self.service.files().list(
            q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id, name)"
        ).execute()
        return response.get('files', [])

    def download_file(self, file_id):
        request = self.service.files().get_media(fileId=file_id)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return buffer.getvalue()

    def create_folder(self, name, parent_id):
        metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        folder = self.service.files().create(body=metadata, fields='id').execute()
        logger.info("Created output folder: " + name)
        return folder['id']

    def upload_file(self, name, data_bytes, mime_type, parent_id):
        metadata = {'name': name, 'parents': [parent_id]}
        media = MediaIoBaseUpload(io.BytesIO(data_bytes), mimetype=mime_type)
        file = self.service.files().create(
            body=metadata, media_body=media, fields='id'
        ).execute()
        logger.info("Uploaded: " + name)
        return file['id']
