"""
gemini_client.py — Gemini API image generation handler.

Uses the gemini-2.0-flash-exp model which accepts an image as input
(your fabric design) and returns generated mock images as output.

The full prompt = [design_image_bytes] + [mock_type_prompt] + [negative_instructions].
Gemini sees your original design and is asked to render it on a specific
garment/product type using the locked prompt.
"""

import time
import google.generativeai as genai
from google.generativeai import types as gtypes

from src.config import GEMINI_API_KEY, GEMINI_MODEL, MAX_RETRIES

# Authenticate once at import time
genai.configure(api_key=GEMINI_API_KEY)


def generate_mock_image(
    design_image_bytes: bytes,
    design_mime_type: str,
    mock_prompt: str,
    negative_prompt: str,
    retry_count: int = 0,
) -> bytes | None:
    """
    Send the fabric design image + mock prompt to Gemini and return
    the generated mock image as raw bytes.

    Args:
        design_image_bytes: Raw bytes of the original fabric design image.
        design_mime_type:   MIME type of the design image, e.g. "image/jpeg".
        mock_prompt:        The full text prompt for this mock type.
        negative_prompt:    Instructions on what to avoid.
        retry_count:        Internal counter for recursive retries (do not set manually).

    Returns:
        Raw bytes of the generated image, or None if all retries failed.
    """
    full_prompt = (
        f"{mock_prompt}\n\n"
        f"IMPORTANT CONSTRAINTS — {negative_prompt}\n\n"
        "Generate ONLY the final product mock image. No text, no explanation."
    )

    try:
        model = genai.GenerativeModel(model_name=GEMINI_MODEL)

        response = model.generate_content(
            contents=[
                gtypes.Part.from_bytes(data=design_image_bytes, mime_type=design_mime_type),
                full_prompt,
            ],
            generation_config=gtypes.GenerationConfig(
                response_modalities=["IMAGE"],
                temperature=0.4,
            ),
        )

        # Extract the first image part from the response
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                return part.inline_data.data

        raise ValueError("Gemini returned a response but no image data was found in it.")

    except Exception as exc:
        if retry_count < MAX_RETRIES - 1:
            wait = 2 ** retry_count * 3
            time.sleep(wait)
            return generate_mock_image(design_image_bytes, design_mime_type, mock_prompt, negative_prompt, retry_count + 1)
        else:
            return None


def get_image_mime_type(filename: str) -> str:
    ext = filename.lower().split(".")[-1]
    mapping = {"jpg":"image/jpeg","jpeg":"image/jpeg","png":"image/png","webp":"image/webp","tiff":"image/tiff","bmp":"image/bmp"}
    return mapping.get(ext, "image/jpeg")
