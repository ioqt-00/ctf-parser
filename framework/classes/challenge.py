from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path

class Challenge:
    def __init__(self,
                id: int,
                category: str,
                name: str,
                points: int,
                description: str,
                files: Optional[List[Path]]
            ) -> None:
        self.id = id
        self.category = category
        self.name = name
        self.points = points
        self.description = description
        self.files = list(files)

        self.solved: bool = False
        self.flag: str = ""
        self.directory: Optional[Path] = None
