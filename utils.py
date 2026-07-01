from pydantic import BaseModel
from typing import List, Optional

class Turn(BaseModel):
    role: str
    text: str


class Chat1_input_demo(BaseModel): 
    sender_id: str # user id
    text: str # user utterance
    image: Optional[str] = None

class Chat1_output_demo(BaseModel):
    text: List[str] # [system utterance]
    score: str 
    is_ending: bool

