"""
Mock Generator — orchestrates downloading a design image, generating 4 mocks via Gemini,
and uploading results to the output folder in Google Drive.
"""

import logging
import time
from src.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

MOCK_TYPES = [
    ("fabric_roll",  "mock_01_fabric_roll"),
    ("maxi_dress",   "mock_02_maxi_dress"),
    ("aerial_drape", "mock_03_aerial_drape"),
    ("flat_lay",     "mock_04_flat_lay"),
]

GEMINI_DELAY_SECONDS = 2


class MockGenerator:
    def __init__(self, config, drive_client):
        self.config = config
        self.drive = drive_client
        self.gemini = GeminiClient(config)

    def generate_mocks(self, design_file):
        file_id = design_file['id']
        file_name = design_file['name']
        base_name = file_name.rsplit('.', 1)[0]

        logger.info(f"Downloading design: {file_name}")
        image_bytes = self.drive.download_file(file_id)

        output_folder_id = self.drive.create_folder(
            base_name, self.config.drive_output_folder_id
        )

        for mock_type, mock_suffix in MOCK_TYPES:
            output_filename = f"{base_name}_{mock_suffix}.jpg"

            try:
                mock_bytes = self.gemini.generate_mock(image_bytes, mock_type)
                self.drive.upload_file(
                    name=output_filename,
                    data_bytes=mock_bytes,
                    mime_type="image/jpeg",
                    parent_id=output_folder_id
                )
                logger.info(f"  Saved: {output_filename}")
            except Exception as e:
                logger.error(f"  Failed {output_filename}: {e}")
                raise

            time.sleep(GEMINI_DELAY_SECONDS)

        logger.info(f"Completed all 4 mocks for: {base_name}")
