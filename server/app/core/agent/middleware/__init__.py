from pydantic import BaseModel

class Context(BaseModel):
  user_name: str