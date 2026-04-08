"""
Configuration loader — reads from environment variables or .env file.
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self.google_service_account_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.drive_input_folder_id = os.environ.get("DRIVE_INPUT_FOLDER_ID")
        self.drive_output_folder_id = os.environ.get("DRIVE_OUTPUT_FOLDER_ID")
        self.gemini_model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-exp")

    def validate(self):
        missing = []
        if not self.google_service_account_json:
            missing.append("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        if not self.drive_input_folder_id:
            missing.append("DRIVE_INPUT_FOLDER_ID")
        if not self.drive_output_folder_id:
            missing.append("DRIVE_OUTPUT_FOLDER_ID")

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        try:
            json.loads(self.google_service_account_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON: {e}")
