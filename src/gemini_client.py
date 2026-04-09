import logging
import io
from huggingface_hub import InferenceClient
from PIL import Image

logger = logging.getLogger(__name__)

MOCK_PROMPTS = {
    "fabric_roll": "Professional commercial product photograph of an elegant patterned textile fabric roll on clean white surface, slightly unrolled to display the pattern, studio lighting, photorealistic, high quality",
    "maxi_dress": "Professional fashion photograph of an elegant maxi dress with decorative fabric pattern on a mannequin, white studio background, soft lighting, high fashion style, full length dress",
    "aerial_drape": "Professional overhead aerial flat-lay photograph of decorative patterned fabric draped softly with gentle folds on pure white background, shot from directly above, soft natural lighting",
    "flat_lay": "Professional flat-lay product photograph of decorative patterned fabric laid completely flat on pure white background, pattern fully visible, no shadows, clean commercial photography",
}


class GeminiClient:
    def __init__(self, config):
        self.hf_client = InferenceClient(token=config.hf_token)

    def generate_mock(self, image_bytes, mock_type):
        prompt = MOCK_PROMPTS[mock_type]
        logger.info("Generating " + mock_type + " via HuggingFace FLUX...")
        result = self.hf_client.text_to_image(
            prompt, model="black-forest-labs/FLUX.1-schnell"
        )
        buffer = io.BytesIO()
        result.save(buffer, format="JPEG", quality=90)
        return buffer.getvalue()
