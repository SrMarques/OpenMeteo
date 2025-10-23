from options.docs import tags_metadata
from options.option import TITLE, DESCRIPTION, VERSION
from routers.weather import weather_data
from routers.stats import temperature_stats, rain_stats, general_stats
from fastapi import FastAPI, Depends, Query, HTTPException
from db.database import engine, get_session

app = FastAPI(
    title=TITLE,
    description=DESCRIPTION, 
    version=VERSION,
    openapi_url="/api/v1/openapi.json",
    openapi_tags=tags_metadata,
    redoc_url=None,
    docs_url="/",
    contact={
        "name": "Miguel Morera",
        "url": "https://www.linkedin.com/in/miguelmoreram",
        "email": "miguelmorera01@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }
)

@app.on_event("startup")
async def on_startup():
    """
    Crear las tablas de la base de datos cuando se inicia la aplicación.

    Se utiliza para crear las tablas de la base de datos en la base de datos configurada en la variable de entorno DATABASE_URL.

    No devuelve nada, solo se encarga de crear las tablas de la base de datos.
    """

    # Conectar a la base de datos
    async with engine.begin() as conn:
        # importar el modelo solo si se necesita
        from db.database import Base
        
        # Crear las tablas segun el modelo
        await conn.run_sync(Base.metadata.create_all)

# Resto de tus rutas
app.include_router(weather_data)
app.include_router(temperature_stats)
app.include_router(rain_stats)
app.include_router(general_stats)