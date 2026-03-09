from pydantic import BaseModel, Field
from typing import Literal

class Params(BaseModel):
    type: Literal["form", "text", "dropdown"]
    paramName: str

print(Params(type="dropdown", paramName="test"))
