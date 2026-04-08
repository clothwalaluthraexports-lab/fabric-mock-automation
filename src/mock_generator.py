"""
mock_generator.py — Core processing loop.

For each design image in the Drive input folder:
  1. Check if already processed (skip if yes)
  2. Download the design image bytes
  3. Create an output subfolder named after the design
  4. For each of the 4 mock types, call Gemini and upload the result
  5. Mark the source file as processed (move to _Processed)
  6. Log the result (success or failure per mock)
  7. Continue to the next design file
"""

import time
from pathlib import Path

from src.config import DELAY_BETWEEN_DESIGNS,MOCK_TYPES,MOVE_PROCESSED_FILES,OUTPUT_FORMAT
from src.drive_client import already_processed_names,download_file_bytes,get_or_create_output_subfolder,list_input_images,move_to_processed,upload_mock_image
from src.gemini_client import generate_mock_image,get_image_mime_type
from src.utils import LogEntry,build_output_filename,get_design_base_name,print_progress


def run_batch() -> list:
    log = []
    print("\n" + "=" * 60)
    print("  FABRIC MOCK AUTOMATION — Starting batch run")
    print("=" * 60)

    print("\n[1/4] Reading input folder from Google Drive...")
    input_files = list_input_images()
    if not input_files:
        print("  No image files found. Exiting.")
        return log
    print(f"  Found {len(input_files)} image file(s).")

    print("[2/4] Checking for already-processed designs...")
    done_names = already_processed_names()
    pending_files = [f for f in input_files if get_design_base_name(f["name"]) not in done_names]
    if not pending_files:
        print("  All designs already processed.")
        return log
    print(f"  {len(pending_files)} design(s) pending.")
    print(f"\n[3/4] Processing designs (4 mocks each)...")

    for idx, file_info in enumerate(pending_files, start=1):
        sname = file_info["name"]
        sid = file_info["id"]
        bname = get_design_base_name(sname)
        mime = get_image_mime_type(sname)
        print_progress(idx, len(pending_files), bname)
        try:
            dbytes = download_file_bytes(sid)
        except Exception as e:
            log.append(LogEntry(design_name=bname,mock_id="ALL",mock_label="Download failed",status="FAILED",error=str(e)))
            continue
        try:
            ofid = get_or_create_output_subfolder(bname)
        except Exception as e:
            log.append(LogEntry(design_name=bname,mock_id="ALL",mock_label="Folder failed",status="FAILED",error=str(e)))
            continue
        all_ok = True
        for mock in MOCK_TYPES:
            mid = mock["id"]; mlab = mock["label"]; mp = mock["prompt"]; neg = mock["negative"]
            ofn = build_output_filename(bname, mid, OUTPUT_FORMAT)
            print(f"   → Generating: {mlab}")
            mib = generate_mock_image(dbytes, mime, mp, neg)
            if mib is None:
                log.append(LogEntry(design_name=bname,mock_id=mid,mock_label=mlab,status="FAILED",error="No image from Gemini"))
                all_ok = False; continue
            try:
                uid = upload_mock_image(mib, ofn, ofid)
                log.append(LogEntry(design_name=bname,mock_id=mid,mock_label=mlab,status="SUCCESS",output_filename=ofn,drive_file_id=uid))
            except Exception as e:
                log.append(LogEntry(design_name=bname,mock_id=mid,mock_label=mlab,status="FAILED",error=str(e)))
                all_ok = False
        if MOVE_PROCESSED_FILES and all_ok:
            try: move_to_processed(sid)
            except: pass
        if idx < len(pending_files): time.sleep(DELAY_BETWEEN_DESIGNS)
    return log
