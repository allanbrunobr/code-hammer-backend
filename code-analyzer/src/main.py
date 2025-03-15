import asyncio

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pyctuator.pyctuator import Pyctuator, Endpoints
from datetime import datetime
from .utils import logger, Policy, Environment
from .startup import startup_event

from .routers import user_router, integrations_router, file_quota_router

app = FastAPI(
    title="ChatAgent",
    description=""
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
    return {"message": "Working..."}

api_router = APIRouter(
    prefix="/api/v1",
)
app.add_event_handler("startup", startup_event)
api_router.include_router(user_router)
api_router.include_router(integrations_router)
api_router.include_router(file_quota_router)

app.include_router(api_router)
