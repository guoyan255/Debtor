from typing import Dict, List
from typing_extensions import TypedDict


class State(TypedDict):
    text: str
    data: List[List[Dict]]
    response: str
