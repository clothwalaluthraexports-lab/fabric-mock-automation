import logging
import io
import google.generativeai as genai
from huggingface_hub import InferenceClient
from PIL import Image

logger = logging.getLogger(__name__)

MOCK_STYLES = {
    "fabric_roll": "fabric roll on clean white surface slightly unrolled, studio lighting, commercial product photography, photorealistic, 4K",
    "maxi_dress": "elegant maxi dress on mannequin, white studio background, soft lighting, high fashion photography, full length dress",
    "aerial_drape": "overhead aerial flat-lay, fabric draped with gentle folds on white background, shot from above, soft natural lighting",
    "flat_lay": "flat-lay on pure white background, completely flat fabric, no shadows, clean commercial product photography",
}


class GeminiClient:
    def __init__(self, config):
        genai.configure(api_key=config.gemini_api_key)
        self.vision_model = genai.GenerativeModel("gemini-1.5-flash")
        self.hf_client = InferenceClient(token=config.hf_token)

    def generate_mock(self, image_bytes, mock_type):
        pil_image = Image.open(io.BytesIO(image_bytes))
        logger.info("Analyzing fabric with Gemini vision...")
        desc_response = self.vision_model.generate_content([
            "Describe this fabric in under 40 words: main colors, pattern type, key visual elements.",
            pil_image
        ])
        fabric_desc = desc_response.text.strip()
        logger.info("Fabric: " + fabric_desc)
        style = MOCK_STYLES[mock_type]
        prompt = "Professional product photo. Fabric with " + fabric_desc + ". " + style
        logger.info("Generating " + mock_type + " via HuggingFace FLUX...")
        result = self.hf_client.text_to_image(prompt, model="black-forest-labs/FLUX.1-schnell")
        buffer = io.BytesIO()
        result.save(buffer, format="JPEG", quality=90)
        return buffer.getvalue()
