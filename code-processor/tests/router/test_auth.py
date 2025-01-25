from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.routers import user_router

app = FastAPI()
app.include_router(user_router)
client = TestClient(app)

def test_login():
    response = client.post("/users/token", data={"username": "testuser", "password": "password"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_route():
    login_response = client.post("/users/token", data={"username": "testuser", "password": "password"})
    token = login_response.json()["access_token"]
    response = client.get("/users/profile", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test User"
