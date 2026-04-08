"""
config.py — Central configuration for Fabric Mock Automation.

All mock type definitions, prompt templates, folder naming rules,
and runtime settings live here. Modify mock prompts here only.
"""

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY: str = os.environ["GEMINI_API_KEY"]
DRIVE_INPUT_FOLDER_ID: str = os.environ["DRIVE_INPUT_FOLDER_ID"]
DRIVE_OUTPUT_FOLDER_ID: str = os.environ["DRIVE_OUTPUT_FOLDER_ID"]
GOOGLE_SERVICE_ACCOUNT_JSON: str | None = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_SERVICE_ACCOUNT_FILE: str | None = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
OUTPUT_FORMAT: str = os.getenv("OUTPUT_FORMAT", "jpg").lower()
OUTPUT_MIME: str = "image/jpeg" if OUTPUT_FORMAT == "jpg" else "image/png"
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
DELAY_BETWEEN_DESIGNS = float(os.getenv("DELAY_BETWEEN_DESIGNS", "5"))
MOVE_PROCESSED_FILES = os.getenv("MOVE_PROCESSED_FILES", "true").lower() == "true"
ACCEPTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp")
GEMINI_MODEL = "gemini-2.0-flash-exp"
PROCESSED_SUBFOLDER_NAME = "_Processed"
LOG_FILENAME = "processing_log.csv"

MOCK_TYPES = [
    {
        "id": "mock_01_fabric_roll",
        "label": "Fabric Roll / Bolt",
        "prompt": (
            "You are a professional product photographer specializing in fabric and textile presentation. "
            "Generate a realistic product mock image of this exact fabric printed on a fabric bolt/roll. "
            "The bolt is partially unrolled on a neutral grey studio surface. "
            "The fabric print must appear EXACTLY as in the input image - same colors, same motifs. "
            "Do NOT redesign, reinterpret, or recolor the print."
        ),
        "negative": "Avoid changing print colors, harsh shadows, white backgrounds, any text.",
    },
    {
        "id": "mock_02_maxi_dress",
        "label": "Women's Maxi Dress on Model",
        "prompt": (
            "You are a professional fashion photographer. "
            "Generate a fashion catalog mock of a women's sleeveless maxi dress made from this exact fabric. "
            "A female model wears the dress, full body shot on soft grey studio background. "
            "The fabric print must appear EXACTLY on the dress - same colors, same motifs. "
            "Do NOT redesign, reinterpret, or recolor the print."
        ),
        "negative": "Avoid changing print design, dark backgrounds, cartoon style, any text.",
    },
    {
        "id": "mock_03_aerial_drape",
        "label": "Aerial Fabric Drape",
        "prompt": (
            "You are a professional fabric lifestyle photographer. "
            "Generate an overhead/aerial mock of this fabric being spread out by a woman (visible from top). "
            "Camera angle 90 degrees overhead. Clean white floor surface. "
            "The fabric print must appear EXACTLY across the spread fabric. "
            "Do NOT redesign, reinterpret, or recolor the print."
        ),
        "negative": "Avoid changing print, dark floors, heavy shadows, any text.",
    },
    {
        "id": "mock_04_flat_lay",
        "label": "Flat Lay Outfit",
        "prompt": (
            "You are a professional e-commerce photographer. "
            "Generate a flat lay mock of a women's outfit made from this exact fabric (top + bottom), "
            "arranged neatly on a pure white surface, camera directly overhead. "
            "The fabric print must appear EXACTLY on both garments. "
            "Do NOT redesign, reinterpret, or recolor the print."
        ),
        "negative": "Avoid changing print, dark surfaces, any model, clutter, any text.",
    },
]
PROCESSED_SUBFOLDER_NAME = "_Processed"
LOG_FILENAME = "processing_log.csv"
