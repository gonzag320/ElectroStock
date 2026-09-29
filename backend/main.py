"""ElectroStock v1.2. Iniciar desde la RAÍZ: python -m uvicorn backend.main:app"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.database.migraciones import preparar_base
from backend.routers import panel, productos, movimientos, categorias, presentaciones


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    preparar_base()
    yield


app = FastAPI(title='ElectroStock API', description='Inventario eléctrico v1.2',
              version='1.2.0', lifespan=lifespan)
for router in [panel.router, categorias.router, productos.router, presentaciones.router, movimientos.router]:
    app.include_router(router)
