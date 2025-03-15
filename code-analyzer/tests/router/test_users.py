from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.domain import User, UserGroup
from src.routers.user import user_router
from src.services.user_service_mock import create_user_mock

app = FastAPI()
app.include_router(user_router)
client = TestClient(app)

def test_create_user():
    response = client.post("/users/", json={
        "username": "ricardo",
        "name": "Ricardo",
        "email": "ricardo@example.com",
        "password": "hashed_password",
        "profile": "User"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Ricardo"
    assert response.json()["profile"] == "User"

def test_read_user():
    # Primeiro, crie um usuário
    create_user_mock(User(
        id="1",
        username="ricardo",
        name="Ricardo",
        email="ricardo@example.com",
        password="hashed_password",
        profile=UserGroup.user,
        disabled=False
    ))

    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Ricardo"
    assert response.json()["profile"] == "User"

def test_update_user():
    create_user_mock(User(
        id="1",
        username="ricardo",
        name="Ricardo",
        email="ricardo@example.com",
        password="hashed_password",
        profile=UserGroup.user,
        disabled=False
    ))

    response = client.put("/users/1", json={
        "username": "ricardo",
        "name": "Ricardão",
        "email": "ricardo@example.com",
        "password": "hashed_password",
        "profile": "User"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Ricardão"
    assert response.json()["profile"] == "User"


def test_list_users():
    create_user_mock(User(
        id="1",
        username="ricardo",
        name="Ricardo",
        email="ricardo@example.com",
        password="hashed_password",
        profile=UserGroup.user,
        disabled=False
    ))

    response = client.get("/users/")
    assert response.status_code == 200
    users = response.json()
    assert len(users) > 0
    assert users[0]["email"] == "ricardo@example.com"
    assert users[0]["profile"] == "User"



def test_delete_user():
    create_user_mock(User(
        id="1",
        username="ricardo",
        name="Ricardo",
        email="ricardo@example.com",
        password="hashed_password",
        profile=UserGroup.user,
        disabled=False
    ))

    response = client.delete("/users/1")
    assert response.status_code == 200
    deleted_user = response.json()
    assert deleted_user["email"] == "ricardo@example.com"

    response_after_deletion = client.get("/users/1")
    assert response_after_deletion.status_code == 404