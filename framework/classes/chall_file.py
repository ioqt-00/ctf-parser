from pathlib import Path
import json

class ChallFile:
    def __init__(self,
            name: str,
            path: Path,
            size: str,
            info: str
            ) -> None:
        self.name = name
        self.path = path
        self.size = size
        self.info = info

    def json(self):
        d = {
            "name": self.name
        }
        return json.dumps(d)
