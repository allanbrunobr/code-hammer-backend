from dotenv import load_dotenv
load_dotenv()
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

from src.routers import conversation_router

app = FastAPI()
app.include_router(conversation_router)

client = TestClient(app)

@pytest.fixture
def conversation_data():
    return {
  "message": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "content": {
      "content_type": "string",
      "parts": "ler historico do Slack"
    },
    "create_time": 0,
    "update_time": 0,
    "metadata": "string"
  },
  "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "parent_message_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "error": "string",
  "mock": False
}

def test_ctrl_conversation(conversation_data):
    headers = {
        "Authorization": "Basic czI0MDUxNDE5MDAtM2FmNjY1MjZlMGEzNDRmZWU2ZjFhMWFjM2ZhMg=="
    }

    with patch('src.services.ConversationService.message', return_value=["data"]) as mock_message:
        response = client.post("/conversation/", json=conversation_data, headers=headers)

        assert response.status_code == 200
        content = response.content

        # Verifique se "data" está presente na resposta
        assert b"data" in content

        # Verifique se o método mock foi chamado uma vez
        mock_message.assert_called_once()