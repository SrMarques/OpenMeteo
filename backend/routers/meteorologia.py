from fastapi import APIRouter, Depends, Query, HTTPException
from models.meteorologiaData import MeteorologiaDataDB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from db.database import get_session, AsyncSessionLocal
from schemas.meteorologia import MeteoDataOut
from services.openmeteo import fetch_weather_data

meteorologia_data = APIRouter()

# Un usuario con la aplicación instalada debe poder ejecutar un comando indicando el nombre de una ciudad y un rango de fechas (inicio y fin). El sistema debe buscar la ciudad usando la Geocoding API de Open-Meteo, obtener su latitud y longitud, y cargar los datos horarios de temperatura y precipitación en su base de datos.

@meteorologia_data.post("/load_weather", tags=["meteorologia_data"])
async def load_weather(city: str, start_date: str, end_date: str):
    """
    Carga datos meteorológicos horarios (temperatura y precipitación)
    desde Open-Meteo para una ciudad y rango de fechas dados.
    """
    try:
        # Obtener datos desde Open-Meteo
        data = await fetch_weather_data(city, start_date, end_date)

        if not data or "hourly" not in data:
            raise HTTPException(status_code=404, detail="No se encontraron datos meteorológicos")

        lat = data.get("latitude")
        lon = data.get("longitude")

        hourly = data["hourly"]
        times = hourly["time"]
        temps = hourly["temperature_2m"]
        precs = hourly["precipitation"]

        # Guardar en base de datos
        async with AsyncSessionLocal() as session:
            for time_str, temp, prec in zip(times, temps, precs):
                dt = datetime.fromisoformat(time_str)  # ✅ conversión segura

                entry = MeteorologiaDataDB(
                    city=city,
                    datetime=dt,
                    temperature_2m=temp,
                    precipitation=prec,
                    latitude=lat,
                    longitude=lon,
                )
                session.add(entry)

            await session.commit()

        return {"message": f"Datos meteorológicos de {city} guardados correctamente.",
                "registros": len(times)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar datos: {str(e)}")



@meteorologia_data.get("/weather/{city}", response_model=list[MeteoDataOut], tags=["meteorologia_data"])
async def get_weather(city: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(MeteorologiaDataDB).where(func.lower(MeteorologiaDataDB.city) == city.lower()))
    data = result.scalars().all()
    if not data:
        raise HTTPException(status_code=404, detail="No hay datos almacenados para esa ciudad")
    return data
