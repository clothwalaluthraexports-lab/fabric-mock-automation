"""
Google Gemini AI client — sends a fabric design image and returns generated mock images.
"""

import logging
import io
from google import genai
from google.genai import types
from PIL import Image

logger = logging.getLogger(__name__)

MOCK_PROMPTS = {
    "fabric_roll": (
        "Generate a professional product photograph of this fabric design printed/woven onto "
        "a fabric roll. The roll should be placed on a clean white or light grey surface, "
        "slightly unrolled to show the pattern clearly. Studio lighting, high quality, "
        "photorealistic style."
    ),
    "maxi_dress": (
        "Generate a professional fashion photograph of a maxi dress made from this fabric design. "
        "Show the full-length dress on a mannequin or model in a clean studio setting. "
        "The fabric pattern should be clearly visible. Elegant, high-fashion style, "
        "white background, soft lighting."
    ),
    "aerial_drape": (
        "Generate a professional overhead/aerial flat-lay photograph of this fabric design "
        "draped softly on a white background. The fabric should have gentle folds and waves "
        "to show texture and movement. Shot from directly above, clean minimal style, "
        "soft natural lighting."
    ),
    "flat_lay": (
        "Generate a professional flat-lay product photograph of this fabric design laid out "
        "completely flat on a pure white background. The pattern should be perfectly visible "
        "with no shadows or distortion. Clean, minimal, commercial photography style."
    ),
}


class GeminiClient:
    def __init__(self, config):
        self.client = genai.Client(api_key=config.gemini_api_key)
        self.model = config.gemini_model

    def generate_mock(self, image_bytes, mock_type):
        prompt = MOCK_PROMPTS[mock_type]
        pil_image = Image.open(io.BytesIO(image_bytes))

        logger.info(f"Generating {mock_type} mock via Gemini...")

        response = self.client.models.generate_content(
            model=self.model,
            contents=[prompt, pil_image],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"]
            )
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                return part.inline_data.data

        raise ValueError(f"Gemini did not return an image for mock type: {mock_type}")
