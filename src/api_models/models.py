from enum import Enum
from pydantic import BaseModel

class Mode(Enum):
    On  = "on"
    Off = "off"

class LightSetter(BaseModel):
    time:str
    mode: Mode
