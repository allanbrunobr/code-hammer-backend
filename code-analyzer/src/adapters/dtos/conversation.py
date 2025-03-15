from pydantic import BaseModel, Field

class ConversationDTO(BaseModel):
    message: str

