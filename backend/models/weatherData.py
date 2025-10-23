from sqlalchemy import Column, Integer, Float, String, DateTime
from db.database import Base

class WeatherDataDB(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False)
    datetime = Column(DateTime, nullable=False)
    temperature_2m = Column(Float)
    precipitation = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)

