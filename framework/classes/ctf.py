from dataclasses import dataclass
from typing import Dict

from framework.classes import Challenge

@dataclass
class Ctf:
    id: int
    name: str
    url: str
    flag_format: str
    challenge_dict: Dict[str, Challenge]
