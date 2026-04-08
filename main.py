"""
main.py — Entry point for Fabric Mock Automation.

Run locally:
    python main.py

Run via GitHub Actions:
    Triggered automatically by the workflow YAML (.github/workflows/run_mock_generator.yml)

What this script does:
    1. Runs the batch mock generation loop
    2. Collects success/failure log entries
    3. Uploads the CSV log to Google Drive
    4. Exits with code 0 (success) or 1 (if any failures occurred)
"""

import sys

from src.mock_generator import run_batch
from src.utils import build_csv_log, print_summary
from src.drive_client import upload_log


def main() -> int:
    """
    Main entry point.
    Returns exit code: 0 = all succeeded, 1 = at least one failure.
    """
    # Run the full batch
    log_entries = run_batch()

    # Print summary to console (visible in GitHub Actions logs)
    print_summary(log_entries)

    # Build and upload the CSV log to Google Drive
    if log_entries:
        print("\n  Uploading processing_log.csv to Google Drive output folder...")
        try:
            csv_content = build_csv_log(log_entries)
            upload_log(csv_content)
            print("  Log uploaded successfully.")
        except Exception as exc:
            print(f"  [WARN] Could not upload log to Drive: {exc}")
            print("  The run still completed — log upload failure is non-fatal.")

    # Determine exit code
    failures = [e for e in log_entries if e.status == "FAILED"]
    if failures:
        print(f"\n  {len(failures)} mock generation(s) failed. Check the log for details.")
        return 1

    print("\n  All mocks generated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
