import os
import argparse

def fn_create(path: str, name: str, value: str):
    if not os.path.exists(path):
        os.makedirs(path)
    
    filename = os.path.join(path, f"{name}.py")

    with open(filename, "w") as handle:
        handle.write(f"""{value.strip()}
""")

def fn_create_dto(name: str):
    path = f"{name}/adapters/dtos"
    fn_create(path, "item", """
from pydantic import BaseModel

class ItemDTO(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
""")
    fn_create(path, "__init__", """
from .item import ItemDTO as ItemDTO
""")
    
def fn_create_service(name: str):
    path = f"{name}/services"
    fn_create(path, "item", """
from ..adapters.dtos import ItemDTO

class ItemService:
    def all(self) -> ItemDTO:
        item = {{
            "name": "Demonstrative item",
            "description": "This is just a demo item",
            "price": 99.99,
            "tax": 10.0
        }}
        return ItemDTO(**item)
""")
    fn_create(path, "__init__", """
from .item import ItemService as ItemService
""")

def fn_create_route(name: str):
    path = f"{name}/routers"
    fn_create(path, "item", """
from fastapi import APIRouter

from ..adapters.dtos import ItemDTO
from ..services import ItemService

router = APIRouter(
    prefix="/items",
    tags=["items"]
)
item = ItemService()

@router.get("/")
def root() -> ItemDTO:
    return item.all()
""")
    fn_create(path, "__init__", "")

def fn_create_main(path: str, title: str, description: str, route: str):
    fn_create(path, "main", f"""
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pyctuator.pyctuator import Pyctuator, Endpoints
from datetime import datetime
from utils import logger, Policy, Environment

from .routers import item

app = FastAPI(
    title="{title}",
    description="{description}"
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
    f"Monitoring {{app.title}} Service",
    app_url=app_url,
    pyctuator_endpoint_url=f"{{app_url}}/actuator",
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
    return {{"message": "Working..."}}

api_router = APIRouter(
    prefix="{route}",
)

api_router.include_router(item.router)

app.include_router(api_router)
""")
    fn_create(path, "__init__", """
__version__ = "0.1.0"

def create_app():
    from .main import app as app

    app.version = __version__

    return app
""")

def init_project(name: str, title: str, description: str, path: str) -> bool:
    if not os.path.exists(f"{name}/__init__.py"):
        fn_create_dto(name)
        fn_create_service(name)
        fn_create_route(name)
        fn_create_main(name, title, description, path)
        fn_create("/", "local", """
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, log_level="debug", reload=True)
""")
        fn_create("/", "main", f"""
from {name} import create_app

app = create_app()
""")
        return True
    
    print("Não será possível inicializar um projeto por já ter um projeto inicializado.")
    return False

def main():
    parser = argparse.ArgumentParser(description="Exemplo de argumentos")
    parser.add_argument("--title", help="Título do aplicativo")
    parser.add_argument("--path", help="Caminho do aplicativo")
    parser.add_argument("--name", default="src", help="Nome do aplicativo")
    parser.add_argument("--description", default="", help="Caminho do aplicativo")

    args = parser.parse_args()

    if args.title and args.path:
        root_path = f"/api{args.path}"

        print(f"""
Criando modelo de aplicação com as seguintes informações:
  Nome: {args.name}
  Título: {args.title}
  Descrição: {args.description}
  Caminho raiz: {root_path}
""")

        error = init_project(args.name, args.title, f"{args.description}", root_path)

        if True == error:
            print("Execução finalizada!")
    else:
        print("Por favor, forneça tanto o nome quanto o caminho do aplicativo.")

if __name__ == "__main__":
    main()
