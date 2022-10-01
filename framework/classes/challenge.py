from typing import Optional, List
from pathlib import Path
import json

from . import ChallFile

class Challenge:
    def __init__(self,
                id: int,
                serverside_id: str,
                category: str,
                name: str,
                points: int,
                description: str,
                solved: bool,
                link: str
            ) -> None:
        self.id = id
        self.serverside_id = serverside_id
        self.category = category
        self.name = name
        self.points = points
        self.description = description
        self.solved = solved
        self.link = link

        self.info = ""
        self.flag: str = ""
        self.directory: Optional[Path] = None
        self.files: list[ChallFile] = []

    def json(self):
        files_dict = {}
        for file in self.files:
            files_dict[file.name] = {
                    "info": file.info,
                    "path": str(file.path),
                    "size": file.size
                }
        d = {
            "id": self.id,
            "category": self.category,
            "name": self.name,
            "points": self.points,
            "description": self.description,
            "files": files_dict,
            "link": self.link,
            "solved": self.solved,
            "flag": self.flag
        }
        return json.dumps(d)
