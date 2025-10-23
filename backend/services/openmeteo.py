import httpx

async def fetch_weather_data(city: str, start_date: str, end_date: str):
    """
    Obtiene lat/lon de la ciudad y los datos meteorológicos desde Open-Meteo.
    """
    async with httpx.AsyncClient() as client:
        # 1️⃣ Buscar ciudad en Geocoding API
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_resp = await client.get(geo_url, params={"name": city, "count": 1, "language": "es"})

        geo_data = geo_resp.json()
        if not geo_data.get("results"):
            return None

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        # 2️⃣ Obtener datos horarios
        meteo_url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": ["temperature_2m", "precipitation"],
            "timezone": "auto"
        }
        meteo_resp = await client.get(meteo_url, params=params)

        return meteo_resp.json()

