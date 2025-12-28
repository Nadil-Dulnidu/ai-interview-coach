from pydantic import BaseModel
from typing import Optional

class Context(BaseModel):
  user_name: Optional[str]
  assistent_name: str