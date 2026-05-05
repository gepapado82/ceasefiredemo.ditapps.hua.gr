from typing import List

from pydantic import BaseModel, conlist


class DetectionObject(BaseModel):
    bbox: conlist(float, min_length=0, max_length=4)
    predicted_class: int
    confidence: float


class Detection(BaseModel):
    imageName: str
    detections: List[DetectionObject]
