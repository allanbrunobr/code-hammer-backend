from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pyctuator.pyctuator import Pyctuator, Endpoints
from datetime import datetime

from .utils import logger, Policy, Environment
from .routers import billing_router, integration_router, plan_router, user_router, subscription_router, pull_request_router, file_quota_router, payment_router
from .core.db import Base, engine


app = FastAPI(
    title="ConfigManager",
    description=""
)
app_url = Environment.get("APPLICATION_URL")
allow_origins = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",  # Alternative local development URL
    "http://localhost:8082",  # Backend URL
    "http://127.0.0.1:8082"   # Alternative backend URL
]

logger.info("Allow origins: %s", str(allow_origins))
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"]
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



Base.metadata.create_all(bind=engine)

api_router.include_router(plan_router)
api_router.include_router(billing_router)
api_router.include_router(integration_router)
api_router.include_router(user_router) # Ensure user_router is included
api_router.include_router(subscription_router)
api_router.include_router(pull_request_router)
api_router.include_router(file_quota_router)
api_router.include_router(payment_router)



app.include_router(api_router)
