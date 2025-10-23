import httpx

async def fetch_weather_data(city: str, start_date: str, end_date: str):
    """
    Fetches datos meteorológicos de una ciudad y rango de fechas.

    Primero, se busca la ciudad en la Geocoding API de Open-Meteo para
    obtener su latitud y longitud. Luego, se obtienen los datos
    horarios de temperatura y precipitación para la ciudad y rango de
    fechas en la API de Archivo de Open-Meteo.

    Parámetros:
        - city (str): nombre de la ciudad
        - start_date (str): fecha de inicio en formato YYYY-MM-DD
        - end_date (str): fecha de fin en formato YYYY-MM-DD

    Devuelve un objeto dict con los datos horarios.
    """
    async with httpx.AsyncClient() as client:
        # Buscar ciudad en Geocoding API
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_resp = await client.get(geo_url, params={"name": city, "count": 1, "language": "es"})

        # formatear a json
        geo_data = geo_resp.json()

        # si no hay resultados None
        if not geo_data.get("results"):
            return None

        # Obtener latitud y longitud
        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        # Obtener datos horarios
        meteo_url = "https://archive-api.open-meteo.com/v1/archive"

        # preparar parámetros de la consulta
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": ["temperature_2m", "precipitation"],
            "timezone": "auto"
        }

        # realizar la consulta
        meteo_resp = await client.get(meteo_url, params=params)

        return meteo_resp.json()

