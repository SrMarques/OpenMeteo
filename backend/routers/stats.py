from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import pandas as pd
from datetime import datetime
from typing import Optional, Dict
from db.database import get_session
from models.weatherData import WeatherDataDB

temperature_stats = APIRouter()
rain_stats = APIRouter()
general_stats = APIRouter()

@temperature_stats.get("/stats/temperature", tags=["temperature_stats"])
async def get_temperature_stats(
    city: str,
    start_date: str,
    end_date: str,
    threshold_high: Optional[float] = Query(30.0, description="Umbral superior de temperatura"),
    threshold_low: Optional[float] = Query(0.0, description="Umbral inferior de temperatura"),
    session: AsyncSession = Depends(get_session)
) -> Dict:
    """
    Estadísticas de temperatura para una ciudad y rango de fechas dados.

    Estas estadísticas incluyen la temperatura promedio, la temperatura promedio por día, la temperatura máxima y mínima, y el número de horas por encima/por debajo del umbral.

    Parámetros:
        - city (str): Ciudad para la que se desean obtener las estadísticas.
        - start_date (str): Fecha de inicio del rango de fechas.
        - end_date (str): Fecha de fin del rango de fechas.
        - threshold_high (Optional[float]): Umbral superior de temperatura. Por defecto, 30.0.
        - threshold_low (Optional[float]): Umbral inferior de temperatura. Por defecto, 0.0.

    Devuelve un objeto dict: con las siguientes estadísticas:
        - temperature (dict): Diccionario con las estadísticas de temperatura.
        - average (float): Promedio de temperatura.
        - average_by_day (dict): Promedio de temperatura por día.
        - max (dict): Diccionario con la temperatura máxima y su fecha.
        - min (dict): Diccionario con la temperatura mínima y su fecha.
        - hours_above_threshold (int): Número de horas por encima del umbral.
        - hours_below_threshold (int): Número de horas por debajo del umbral.
    """

    # convertir fechas a datetime o error de formato
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    # Obtener datos de la DB
    result = await session.execute(
        select(WeatherDataDB)
        .where(func.lower(WeatherDataDB.city) == city.lower())
        .where(WeatherDataDB.datetime >= start_dt)
        .where(WeatherDataDB.datetime <= end_dt)
    )
    data = result.scalars().all()

    # Comprobar que haya datos sino 404
    if not data:
        raise HTTPException(status_code=404, detail="En la Base de datos LOCAL, no hay datos para esa ciudad y rango de fechas")

    # Convertir a DataFrame
    df = pd.DataFrame([{
        "datetime": d.datetime,
        "temperature": d.temperature_2m
    } for d in data])

    # Estadísticas generales
    average_temp = df["temperature"].mean()
    max_row = df.loc[df["temperature"].idxmax()]
    min_row = df.loc[df["temperature"].idxmin()]

    # Promedio por día
    df["date"] = df["datetime"].dt.date
    average_by_day = df.groupby("date")["temperature"].mean().round(2).to_dict()

    # Horas por encima / debajo del umbral
    hours_above = (df["temperature"] > threshold_high).sum()
    hours_below = (df["temperature"] < threshold_low).sum()

    # Devolver estadísticas con el formato requerido
    return {
        "temperature": {
            "average": round(average_temp, 2),
            "average_by_day": {str(k): v for k, v in average_by_day.items()},
            "max": {
                "value": max_row["temperature"],
                "date_time": max_row["datetime"].isoformat()
            },
            "min": {
                "value": min_row["temperature"],
                "date_time": min_row["datetime"].isoformat()
            },
            "hours_above_threshold": int(hours_above),
            "hours_below_threshold": int(hours_below)
        }
    }


@rain_stats.get("/stats/precipitation", tags=["rain_stats"])
async def get_precipitation_stats(
    city: str,
    start_date: str,
    end_date: str,
    session: AsyncSession = Depends(get_session)
) -> Dict:
   
    
    # Convertir fechas a datetime
    """
    Estadísticas de precipitación para una ciudad y rango de fechas.

    Parámetros:
        - city (str): nombre de la ciudad
        - start_date (str): fecha de inicio en formato YYYY-MM-DD
        - end_date (str): fecha de fin en formato YYYY-MM-DD

    Devuelve un objeto dict: con las siguientes estadísticas:
        - total: suma de la precipitación en el rango de fechas
        - total_by_day: objeto con la suma de la precipitación por día
        - days_with_precipitation: número de días con precipitación > 0
        - max: objeto con el valor y la fecha de la máxima precipitación
        - average: promedio de la precipitación en el rango de fechas
    """
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    # Ajustar fechas para incluir todo el día
    start_dt = datetime.combine(start_dt.date(), datetime.min.time())
    end_dt = datetime.combine(end_dt.date(), datetime.max.time())

    # Consulta a la DB
    result = await session.execute(
        select(WeatherDataDB)
        .where(func.lower(WeatherDataDB.city) == city.lower())
        .where(WeatherDataDB.datetime >= start_dt)
        .where(WeatherDataDB.datetime <= end_dt)
    )
    data = result.scalars().all()
    
    # Verificar que haya datos
    if not data:
        raise HTTPException(status_code=404, detail="En la Base de datos LOCAL, no hay datos para esa ciudad y rango de fechas")

    # Convertir a DataFrame
    df = pd.DataFrame([{
        "datetime": d.datetime,
        "precipitation": d.precipitation
    } for d in data])
    
    # Total y promedio
    total_precip = df["precipitation"].sum()
    average_precip = df["precipitation"].mean()
    
    # Total por día
    df["date"] = df["datetime"].dt.date
    total_by_day = df.groupby("date")["precipitation"].sum().round(2).to_dict()
    
    # Días con precipitación > 0
    days_with_precip = (df.groupby("date")["precipitation"].sum() > 0).sum()
    
    # Día de máxima precipitación
    max_day_row = df.groupby("date")["precipitation"].sum().idxmax()
    max_value = df.groupby("date")["precipitation"].sum().max()

    return {
        "precipitation": {
            "total": round(total_precip, 2),
            "total_by_day": {str(k): v for k, v in total_by_day.items()},
            "days_with_precipitation": int(days_with_precip),
            "max": {
                "value": round(max_value, 2),
                "date": str(max_day_row)
            },
            "average": round(average_precip, 2)
        }
    }

@general_stats.get("/stats/general", tags=["general_stats"])
async def get_general_stats(session: AsyncSession = Depends(get_session)) -> Dict:
    # Obtener todos los registros de la base de datos
    """
    Estadísticas generales de temperatura y precipitación para todas las ciudades y fechas disponibles.

    Devuelve un objeto dict con las siguientes estadísticas para cada ciudad:
        - start_date (str): fecha de inicio en formato YYYY-MM-DD
        - end_date (str): fecha de fin en formato YYYY-MM-DD
        - temperature_average (float): promedio de la temperatura en el rango de fechas
        - precipitation_total (float): total de la precipitación en el rango de fechas
        - days_with_precipitation (int): número de días con precipitación > 0
        - precipitation_max (dict): objeto con la fecha y el valor de la máxima precipitación
        - temperature_max (dict): objeto con la fecha y el valor de la máxima temperatura
        - temperature_min (dict): objeto con la fecha y el valor de la mínima temperatura
    """
    # Consulta a la DB
    result = await session.execute(select(WeatherDataDB))
    data = result.scalars().all()

    # Verificar que haya datos
    if not data:
        raise HTTPException(status_code=404, detail="No hay datos meteorológicos almacenados")

    # Convertir a DataFrame
    df = pd.DataFrame([{
        "city": d.city,
        "datetime": d.datetime,
        "temperature_2m": d.temperature_2m,
        "precipitation": d.precipitation,
    } for d in data])

    # Verificar que haya datos o lanzar error
    if df.empty:
        raise HTTPException(status_code=404, detail="No hay datos disponibles")

    # parsear datetime a date
    df["date"] = df["datetime"].dt.date

    
    output = {}
    # Agrupar por ciudad (case-insensitive)
    for city, group in df.groupby(df["city"].str.lower()):  
        group_sorted = group.sort_values("datetime")
        start_date = str(group_sorted["date"].min())
        end_date = str(group_sorted["date"].max())

        # Promedio de temperatura
        temp_avg = round(group_sorted["temperature_2m"].mean(), 2)

        # Total de precipitación
        precip_total = round(group_sorted["precipitation"].sum(), 2)

        # Días con precipitación
        days_with_precip = (group_sorted.groupby("date")["precipitation"].sum() > 0).sum()

        # Día de máxima precipitación
        precip_by_day = group_sorted.groupby("date")["precipitation"].sum()
        precip_max_day = precip_by_day.idxmax()
        precip_max_val = round(precip_by_day.max(), 2)

        # Día y valor de máxima temperatura
        temp_max_row = group_sorted.loc[group_sorted["temperature_2m"].idxmax()]
        temp_max_date = str(temp_max_row["datetime"].date())
        temp_max_val = round(temp_max_row["temperature_2m"], 2)

        # Día y valor de mínima temperatura
        temp_min_row = group_sorted.loc[group_sorted["temperature_2m"].idxmin()]
        temp_min_date = str(temp_min_row["datetime"].date())
        temp_min_val = round(temp_min_row["temperature_2m"], 2)

        # Armar salida
        output[group_sorted["city"].iloc[0]] = {
            "start_date": start_date,
            "end_date": end_date,
            "temperature_average": temp_avg,
            "precipitation_total": precip_total,
            "days_with_precipitation": int(days_with_precip),
            "precipitation_max": {
                "date": str(precip_max_day),
                "value": precip_max_val
            },
            "temperature_max": {
                "date": temp_max_date,
                "value": temp_max_val
            },
            "temperature_min": {
                "date": temp_min_date,
                "value": temp_min_val
            }
        }

    return output
