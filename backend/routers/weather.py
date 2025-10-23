from fastapi import APIRouter, Depends, Query, HTTPException
from models.weatherData import WeatherDataDB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from db.database import get_session, AsyncSessionLocal
from schemas.weather import MeteoDataOut
from services.openmeteo import fetch_weather_data

weather_data = APIRouter()

@weather_data.post("/load_weather", tags=["weather_data"])
async def load_weather(city: str, start_date: str, end_date: str):
    """
    Carga de datos meteorológicos.

    Parámetros:
        - city (str): nombre de la ciudad
        - start_date (str): fecha de inicio en formato YYYY-MM-DD
        - end_date (str): fecha de fin en formato YYYY-MM-DD

    Devuelve un objeto dict con el mensaje de éxito y el número de registros
    guardados. Si se produce un error al cargar los datos, se lanzará un
    HTTPException con código 500.
    """
    try:
        # Obtener datos desde Open-Meteo
        data = await fetch_weather_data(city, start_date, end_date)

        # Verificar que haya datos sino error
        if not data or "hourly" not in data:
            raise HTTPException(status_code=404, detail="No se encontraron datos meteorológicos")

        # Obtener latitud y longitud
        lat = data.get("latitude")
        lon = data.get("longitude")

        # Obtener datos horarios
        hourly = data["hourly"]
        times = hourly["time"]

        # Obtener temperaturas y precipitaciones
        temps = hourly["temperature_2m"]
        precs = hourly["precipitation"]

        # Guardar en base de datos
        async with AsyncSessionLocal() as session:
            for time_str, temp, prec in zip(times, temps, precs):
                # Convertir a datetime
                dt = datetime.fromisoformat(time_str)

                # Preparar entry para guardar
                entry = WeatherDataDB(
                    city=city,
                    datetime=dt,
                    temperature_2m=temp,
                    precipitation=prec,
                    latitude=lat,
                    longitude=lon,
                )
                # Guardar
                session.add(entry)

            # Commit para conformar la transacción y cerrar sesión
            await session.commit()

        # Devolver respuesta con la información de los registros
        return {"message": f"Datos meteorológicos de {city} guardados correctamente.",
                "registros": len(times)}

    # Manejar excepciones   
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar datos: {str(e)}")



@weather_data.get("/weather/{city}", response_model=list[MeteoDataOut], tags=["weather_data"])
async def get_weather(city: str, session: AsyncSession = Depends(get_session)):
    """
    Obtiene los datos meteorológicos almacenados para una ciudad.

    Parámetros:
        - city (str): nombre de la ciudad

    Devuelve una lista de objetos MeteoDataOut con los datos meteorológicos
    almacenados. Si no hay datos almacenados para esa ciudad, se lanzará
    un HTTPException con código 404.
    """
    # Consulta a la DB
    result = await session.execute(select(WeatherDataDB).where(func.lower(WeatherDataDB.city) == city.lower()))
    
    # Obtener los datos
    data = result.scalars().all()
    
    # Si no hay datos error
    if not data:
        raise HTTPException(status_code=404, detail="No hay datos almacenados para esa ciudad")
    return data
