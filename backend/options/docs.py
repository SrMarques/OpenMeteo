tags_metadata = [
  {
    "name": "weather_data",
    "description": "<b>Carga de datos meteorológicos.</b> <br/>Un usuario con la aplicación instalada debe poder ejecutar un comando indicando el nombre de una ciudad y un rango de fechas (inicio y fin). <br/>El sistema debe buscar la ciudad usando la Geocoding API de Open-Meteo, obtener su latitud y longitud, y cargar los datos horarios de temperatura y precipitación en su base de datos.",
    "externalDocs": {
            "description": "Carga de datos meteorológicos.",
            "url": "https://fastapi.tiangolo.com/"
        }
  },
  {
    "name": "temperature_stats",
    "description": "<b>Estadísticas de temperatura.</b> <br/>Como usuario con la aplicación ejecutada, debo poder visitar una URL y obtener las siguientes estadísticas de temperatura para una ciudad y rango de fechas",
    "externalDocs": {
            "description": "Estadísticas de temperatura.",
            "url": "https://fastapi.tiangolo.com/"
        }
  },
  {
    "name": "rain_stats",
    "description": "<b>Estadísticas de precipitación.</b> <br/>Como usuario con la aplicación ejecutada, debo poder visitar una URL y obtener las siguientes estadísticas de precipitación para una ciudad y rango de fechas",
    "externalDocs": {
            "description": "Estadísticas de precipitación.",
            "url": "https://fastapi.tiangolo.com/"
        }
  },
  {
    "name": "general_stats",
    "description": "<b>Estadísticas generales.</b> <br/>Como usuario con la aplicación ejecutada, debo poder visitar una URL y obtener las siguientes estadísticas globales para cada ciudad y rango de fechas almacenados",
    "externalDocs": {
            "description": "Estadísticas generales",
            "url": "https://fastapi.tiangolo.com/"
        }
  }
]