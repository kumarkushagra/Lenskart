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
            You are a precision Optical Measurement AI. Analyze the image and output VISUAL MEASUREMENTS as strictly formatted JSON.

            STEP 1: IDENTIFY CONSTRUCTION (Internal Check)
            - Is it RIMLESS? (Lenses bolted directly to bridge/temples, no surrounding material).
            - Is it FULL-RIM? (Material completely encircles the lenses).
            - Is it SEMI-RIM? (Material covers top only).

            STEP 2: APPLY SCORING RULES (Strict Adherence Required)

            1.  Visual Weight (-5.0 to +5.0):
                -   CRITICAL RULE: If Construction is RIMLESS, Score MUST be -5.0 to -4.0.
                -   -5.0 (Invisible/Light): Rimless, drill-mounts, or ultra-thin <1mm wire.
                -   +5.0 (Bold/Heavy): Thick acetate (>4mm), chunky geometric frames, high-contrast black/tortoise.

            2.  Gender Expression (-5.0 to +5.0):
                -   -5.0 (Masculine): Rectangular, square, double-bar aviator, flat browline.
                -   0.0 (Unisex): Round, PANTOS (tea-cup), or oval shapes. Rimless round frames are typically UNISEX.
                -   +5.0 (Feminine): EXAGGERATED Cat-Eye, Butterfly, or Upswept corners.
                -   *Warning*: Do not confuse "Round" with "Cat-Eye". If no material extends upwards at corners, it is NOT Cat-Eye.

            3.  Embellishment (-5.0 to +5.0):
                -   -5.0 (Minimal): Standard functional hinges, unibody metal/plastic, no patterns.
                -   +5.0 (Ornate): Crystals, pearls, filigree engraving, multi-color patterns, non-functional aesthetic hardware.

            4.  Unconventionality (-5.0 to +5.0):
                -   -5.0 (Classic): Timeless shapes (Round, Rectangle, Aviator) in standard colors (Gold, Silver, Black, Tortoise).
                -   +5.0 (Avant-Garde): Asymmetrical, shield/visor styles, neon/transparent colors, octagonal/hexagonal shapes.

            5.  Formality (-5.0 to +5.0):
                -   -5.0 (Casual): Rubberized, colorful plastic, sporty wraps.
                -   +5.0 (Formal): Rimless styles, high-polish gold/silver/bronze, titanium aesthetics.

            VISUAL ATTRIBUTES EXTRACTION:
            - Colors: List the METAL color (Gold/Silver/Bronze) separate from the TIP color (Black/Tortoise).
            - Geometry: Use specific terms: "Round", "Pantos", "Rectangular", "Cat-Eye".

            OUTPUT INSTRUCTIONS:
            - Output ONLY valid JSON matching the schema.
            - No markdown, no conversational text.
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
