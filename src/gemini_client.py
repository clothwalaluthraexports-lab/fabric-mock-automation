import logging
import io
from google import genai
from google.genai import types
from PIL import Image

logger = logging.getLogger(__name__)

MOCK_PROMPTS = {
    "fabric_roll": (
        "Generate a professional product photograph of this fabric design printed onto "
        "a fabric roll on a clean white surface, slightly unrolled to show the pattern. "
        "Studio lighting, high quality, photorealistic."
    ),
    "maxi_dress": (
        "Generate a professional fashion photograph of a maxi dress made from this fabric. "
        "Full-length dress on a mannequin, clean studio, white background, soft lighting."
    ),
    "aerial_drape": (
        "Generate a professional overhead flat-lay of this fabric draped softly on white. "
        "Gentle folds to show texture, shot from directly above, soft natural lighting."
    ),
    "flat_lay": (
        "Generate a professional flat-lay of this fabric laid completely flat on white. "
        "Pattern fully visible, no shadows, clean commercial photography style."
    ),
}


class GeminiClient:
    def __init__(self, config):
        self.client = genai.Client(
            api_key=config.gemini_api_key,
            http_options={'api_version': 'v1alpha'}
        )
        self.model = config.gemini_model

    def generate_mock(self, image_bytes, mock_type):
        prompt = MOCK_PROMPTS[mock_type]
        pil_image = Image.open(io.BytesIO(image_bytes))
        logger.info("Generating " + mock_type + " mock via Gemini...")
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
        raise ValueError("Gemini did not return an image for: " + mock_type)
