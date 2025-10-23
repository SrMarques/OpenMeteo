from fastapi import FastAPI
from options.docs import tags_metadata
from options.option import TITLE, DESCRIPTION, VERSION
from routers.meteorologia import meteorologia_data
from routers.stats import temperatura_stats, lluvia_stats, general_stats
    
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

# Resto de tus rutas
app.include_router(meteorologia_data)
app.include_router(temperatura_stats)
app.include_router(lluvia_stats)
app.include_router(general_stats)