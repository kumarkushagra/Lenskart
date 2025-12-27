from typing import Literal, List
from pydantic import BaseModel, Field
from ollama import Client
import requests
import base64
import time


# defining the json schema using BaseModel

class VisualDimension(BaseModel):
    score: float = Field(ge=-5.0, le=5.0)
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


class VisualDimensions(BaseModel):
    gender_expression: VisualDimension
    visual_weight: VisualDimension
    embellishment: VisualDimension
    unconventionality: VisualDimension
    formality: VisualDimension


class VisualAttributes(BaseModel):
    wireframe_present: Literal[True, False, "NILL"]
    frame_geometry: Literal[
        "round", "rectangular", "square", "aviator",
        "cat_eye", "irregular", "NIL"
    ]
    transparency: Literal[
        "low", "medium", "high", "opaque", "NIL"
    ]
    dominant_colors: List[str]
    surface_texture: Literal[
        "smooth", "matte", "glossy", "patterned", "NIL"
    ]
    suitable_for_kids: Literal["yes", "no", "ambiguous"]


class VisualMetadata(BaseModel):
    image_clarity: Literal["clear", "blurry", "low_resolution", "NIL"]
    view_angle: Literal["front", "side", "angled", "multiple", "NIL"]
    lighting_condition: Literal["even", "harsh", "dim", "uneven", "NIL"]


class ImageAnalysis(BaseModel):
    visual_dimensions: VisualDimensions
    visual_attributes: VisualAttributes
    visual_metadata: VisualMetadata
    ambiguities: List[str]


# testing the image processing
 
def analyze_image(image_url: str):
    client = Client(host="http://localhost:11434")

    # ---- Fetch image ----
    try:
        resp = requests.get(image_url, timeout=8)
        resp.raise_for_status()
    except Exception as e:
        return {
            "visual_dimensions": None,
            "visual_attributes": None,
            "visual_metadata": None,
            "ambiguities": ["Image URL unreachable"],
            "error_summary": str(e),
        }

    # ---- Base64 encoding ----
    img_b64 = base64.b64encode(resp.content).decode("utf-8")

    # ---- Prompt ----
    prompt = """
    You are an emplpoyee at a vision care store, you have to classify the eyeglasses correctly,
    Analyze the image and return ONLY valid JSON matching the schema.

    You are performing VISUAL MEASUREMENT, not classification.

    CRITICAL RULES:
    - Use ONLY visually observable cues.
    - Do NOT infer brand, price, intent, or user.
    - Choose ONLY allowed enum values.
    - Include ALL required fields.
    - Return STRICT JSON only.

    SCORING INSTRUCTIONS (IMPORTANT):
    - Scores must reflect RELATIVE visual strength, not certainty.
    - 0.0 is allowed ONLY if two opposing visual cues clearly cancel out.
    - If a dimension leans even slightly in one direction, you MUST use a non-zero score.
    - Use these bands:
      - ±0.5 to ±1.0 : slight but visible lean
      - ±1.5 to ±2.5 : clear visual lean
      - ±3.0 to ±4.5 : strong visual expression
    - Do NOT assign 0.0 to all dimensions.

    CONFIDENCE RULES:
    - Confidence reflects clarity of visual evidence, not strength of score.

    REASONING RULES:
    - Each dimension MUST have distinct reasoning.
    - Reasoning must cite specific visual cues (shape, thickness, color, geometry).

    DIMENSION DEFINITIONS:
    - Gender Expression: masculine (-5) and feminine (+5)
    - Visual Weight: light (-5) && heavy (+5)
    - Embellishment: simple (-5) && ornate (+5)
    - Unconventionality: classic (-5) && avant-garde (+5)
    - Formality: casual (-5) && formal (+5)

    Return a proper JSON.
    """

    #Sending the request to Ollama server
    response = client.chat(
        model="gemma3:4b", #picked a small model (i have internet plan of 40Mbps :( )
        format=ImageAnalysis.model_json_schema(),
        messages=[
            {
                "role": "user",
                "content": prompt,
                "images": [img_b64],
            }
        ],
        options={"temperature": 0},
    )

    result = ImageAnalysis.model_validate_json(response["message"]["content"])

    return result.model_dump_json(indent=2) 


if __name__ == "__main__":
    IMAGE_URL = "https://static5.lenskart.com/media/catalog/product/pro/1/thumbnail/1325x636/9df78eab33525d08d6e5fb8d27136e95//l/i/lenskart-lk-e17571me-s57-dark-gunmetal-eyeglasses_dsc1394_15_11_2024.jpg"
    print(analyze_image(IMAGE_URL))
