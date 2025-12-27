from pydantic import BaseModel, Field
from typing import Literal, List

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
    wireframe_present: Literal[True, False, "ambiguous"]
    frame_geometry: Literal[
        "round", "rectangular", "square", "aviator",
        "cat_eye", "irregular", "unknown"
    ]
    transparency: Literal[
        "low", "medium", "high", "opaque", "unknown"
    ]
    dominant_colors: List[str]
    surface_texture: Literal[
        "smooth", "matte", "glossy", "patterned", "unknown"
    ]
    suitable_for_kids: Literal["yes", "no", "ambiguous"]


class VisualMetadata(BaseModel):
    image_clarity: Literal["clear", "blurry", "low_resolution", "unknown"]
    view_angle: Literal["front", "side", "angled", "multiple", "unknown"]
    lighting_condition: Literal["even", "harsh", "dim", "uneven", "unknown"]


class ImageAnalysis(BaseModel):
    visual_dimensions: VisualDimensions
    visual_attributes: VisualAttributes
    visual_metadata: VisualMetadata
    ambiguities: List[str]
