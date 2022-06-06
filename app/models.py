import json
from typing import Dict


class Label:
    def __init__(self, text: str, type: str):
        self.text = text
        self.type = type

    def toJSON(self):
        return json.dumps(
            self, default=lambda o: o.__dict__, sort_keys=True, indent=4
        )


class Competency:
    def __init__(
        self,
        competencyType: str,
        conceptType: str,
        conceptUri: str,
        description: str,
        id: int = -1,
        labels: Label = None,
    ):
        self.id = id
        self.competencyType = competencyType
        self.conceptType = conceptType
        self.conceptUri = conceptUri
        self.description = description
        self.labels = labels

    def toJSON(self) -> Dict:
        return {
            "id": self.id,
            "competencyType": self.competencyType,
            "conceptType": self.conceptType,
            "conceptUri": self.conceptUri,
            "description": self.description,
        }


class Course:
    def __init__(self, id: int, description: str):
        self.id = id
        self.description = description

    def toJSON(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
        }
