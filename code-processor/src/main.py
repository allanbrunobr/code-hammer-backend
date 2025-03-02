from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pyctuator.pyctuator import Pyctuator, Endpoints
from datetime import datetime

from .utils import logger, Policy, Environment
from .routers import process, analysis
from .core.db import Base, engine

app = FastAPI(
    title="CodeProcessor",
    description="API para processamento e análise de código"
)
app_url = Environment.get("APPLICATION_URL")
allow_origins = Policy.origins(app_url)

logger.info("Allow origins: %s", str(allow_origins))
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Pyctuator(
    app,
    f"Monitoring {app.title} Service",
    app_url=app_url,
    pyctuator_endpoint_url="/actuator",
    registration_url=None,
    metadata=dict(
        statup=datetime.now().date()
    ),
    disabled_endpoints=[
        Endpoints.ENV,
        Endpoints.THREAD_DUMP,
        Endpoints.LOGFILE
    ]
)

@app.get("/", include_in_schema=False)
def root():
    return {
        "message": "CodeProcessor API is running",
        "version": "1.0.0",
        "documentation": "/docs"
    }

api_router = APIRouter(
    prefix="/api/v1",
)

# Inicializar banco de dados
Base.metadata.create_all(bind=engine)

# Registrar routers
api_router.include_router(process.process_router)
api_router.include_router(analysis.analysis_router)

app.include_router(api_router)
