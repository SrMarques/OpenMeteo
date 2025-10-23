from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de la base de datos
DATABASE_URL = "sqlite+aiosqlite:///./openmeteo.db"

# Configuración de la base de datos
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Configuración de la sesión
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# base de datos
Base = declarative_base()

# Obtención de sesión queda abierta hasta salir de la función gracias a yield
async def get_session():
    """
    Obtiene una sesión de base de datos.

    La sesión se abre en cuanto se llama a esta función y se cierra cuando se sale de la función.

    :yield: 

    :rtype: AsyncSession 
    """
    async with AsyncSessionLocal() as session:
        yield session