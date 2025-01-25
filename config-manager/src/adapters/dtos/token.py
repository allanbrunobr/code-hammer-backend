from pydantic import BaseModel

class Token(BaseModel):
    username: str