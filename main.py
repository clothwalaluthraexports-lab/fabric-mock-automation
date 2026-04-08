"""
Fabric Mock Automation - Main Entry Point
"""

import sys
import logging
from src.config import Config
from src.drive_client import DriveClient
from src.mock_generator import MockGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting Fabric Mock Automation...")

    config = Config()
    config.validate()

    drive_client = DriveClient(config)
    mock_generator = MockGenerator(config, drive_client)

    logger.info("Scanning input folder...")
    design_files = drive_client.list_image_files(config.drive_input_folder_id)

    if not design_files:
        logger.info("No image files found in input folder. Nothing to process.")
        return

    logger.info(f"Found {len(design_files)} design image(s) to process.")

    processed = drive_client.list_subfolders(config.drive_output_folder_id)
    processed_names = {f['name'] for f in processed}

    success_count = 0
    skip_count = 0
    error_count = 0

    for design_file in design_files:
        design_name = design_file['name'].rsplit('.', 1)[0]

        if design_name in processed_names:
            logger.info("Skipping already processed: " + design_name)
            skip_count += 1
            continue

        logger.info("Processing: " + design_file['name'])
        try:
            mock_generator.generate_mocks(design_file)
            success_count += 1
        except Exception as e:
            logger.error("Failed to process " + design_file['name'] + ": " + str(e))
            error_count += 1

    logger.info("Done! Processed: " + str(success_count) + ", Skipped: " + str(skip_count) + ", Errors: " + str(error_count))

    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()"""
Fabric Mock Automation - Main Entry Point
"""

import sys
import logging
from src.config import Config
from src.drive_client import DriveClient
from src.mock_generator import MockGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting Fabric Mock Automation...")

    config = Config()
    config.validate()

    drive_client = DriveClient(config)
    mock_generator = MockGenerator(config, drive_client)

    logger.info("Scanning input folder...")
    design_files = drive_client.list_image_files(config.drive_input_folder_id)

    if not design_files:
        logger.info("No image files found in input folder. Nothing to process.")
        return

    logger.info(f"Found {len(design_files)} design image(s) to process.")

    processed = drive_client.list_subfolders(config.drive_output_folder_id)
    processed_names = {f['name'] for f in processed}

    success_count = 0
    skip_count = 0
    error_count = 0

    for design_file in design_files:
        design_name = design_file['name'].rsplit('.', 1)[0]

        if design_name in processed_names:
            logger.info("Skipping already processed: " + design_name)
            skip_count += 1
            continue

        logger.info("Processing: " + design_file['name'])
        try:
            mock_generator.generate_mocks(design_file)
            success_count += 1
        except Exception as e:
            logger.error("Failed to process " + design_file['name'] + ": " + str(e))
            error_count += 1

    logger.info("Done! Processed: " + str(success_count) + ", Skipped: " + str(skip_count) + ", Errors: " + str(error_count))

    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
