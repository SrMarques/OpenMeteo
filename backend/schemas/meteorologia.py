from pydantic import BaseModel
from datetime import datetime

class MeteoDataOut(BaseModel):
    city: str
    datetime: datetime
    temperature_2m: float
    precipitation: float
    latitude: float
    longitude: float

    class Config:
        orm_mode = True
