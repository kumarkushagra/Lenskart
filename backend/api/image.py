import asyncio
import requests
import tempfile
import os
import urllib3
from ollama import AsyncClient
from schema import *  # importing schemas from schema.py

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ImageAnalyzer:
    def __init__(self, ollama_host: str = None, model: str = "gemma3:4b", timeout: int = 8):
        if ollama_host is None:
            ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.client = AsyncClient(host=ollama_host)
        self.model = model
        self.timeout = timeout

    def fetch_image_to_temp(self, image_url: str) -> str:
        try:
            resp = requests.get(image_url,timeout=self.timeout,verify=False)
            resp.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Image fetch failed: {e}")

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        tmp.write(resp.content)
        tmp.close()

        return tmp.name

    async def process_json(self, image_path: str) -> ImageAnalysis:
        prompt = """
            Analyze the image and return ONLY valid JSON matching the schema.

            You are performing VISUAL MEASUREMENT of eyeglasses.
            This is NOT classification, recommendation, or merchandising.

            RULES:
            - Use ONLY visually observable cues.
            - Do NOT infer brand, price, intent, user, or quality.
            - Choose ONLY allowed enum values.
            - Include ALL required fields.
            - Return STRICT JSON only.

            SCORING:
            - Scores represent RELATIVE visual strength.
            - 0.0 allowed ONLY if opposing cues cancel out.
            - If any lean exists, use a non-zero score.
            - At least TWO dimensions MUST be non-zero.

            BANDS:
            - ±0.5 to ±1.0 : slight lean
            - ±1.5 to ±2.5 : clear lean
            - ±3.0 to ±4.5 : strong expression

            DIMENSIONS:
            - Gender Expression: masculine (-5) → feminine (+5)
            - Visual Weight: light (-5) → heavy (+5)
            - Embellishment: simple (-5) → ornate (+5)
            - Unconventionality: classic (-5) → avant-garde (+5)
            - Formality: casual (-5) → formal (+5)

            Return JSON only.
        """

        full_response = ""

        async for part in await self.client.generate(
            model=self.model,
            prompt=prompt,
            images=[image_path],
            format=ImageAnalysis.model_json_schema(),
            options={"temperature": 0},
            stream=True,
        ):
            full_response += part["response"]

        return ImageAnalysis.model_validate_json(full_response)

    async def run(self, image_url: str) -> dict:
        image_path = self.fetch_image_to_temp(image_url)

        try:
            result = await self.process_json(image_path)
        finally:
            # ALWAYS clean up temp file
            if os.path.exists(image_path):
                os.remove(image_path)

        return result.model_dump_json(indent=2)


if __name__ == "__main__":
    IMAGE_URL = (
        "https://static5.lenskart.com/media/catalog/product/pro/1/thumbnail/1325x636/9df78eab33525d08d6e5fb8d27136e95//l/i/lenskart-lk-e17571me-s57-dark-gunmetal-eyeglasses_dsc1394_15_11_2024.jpg"
    )

    async def main():
        analyzer = ImageAnalyzer()
        result = await analyzer.run(IMAGE_URL)
        print(result)

    asyncio.run(main())
