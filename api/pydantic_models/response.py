from pydantic import BaseModel

from .detection import Detection


class DetResponse(BaseModel):
    results: list[Detection]


class DetResponseWithTime(DetResponse):
    time: float
