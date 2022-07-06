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
        skillType: str,
        conceptType: str,
        conceptUri: str,
        reuseLevel: str,
        preferredLabel: str,
        altLabels: str,
        hiddenLabels: str,
        status: str,
        modifiedDate: str,
        scopeNote: str,
        definition: str,
        inScheme: str,
        description: str,
        id: int = -1,
        labels: Label = None,
    ):
        self.id = id
        self.skillType = skillType
        self.conceptType = conceptType
        self.conceptUri = conceptUri
        self.reuseLevel = reuseLevel
        self.preferredLabel = preferredLabel
        self.altLabels = altLabels
        self.hiddenLabels = hiddenLabels
        self.status = status
        self.modifiedDate = modifiedDate
        self.scopeNote = scopeNote
        self.definition = definition
        self.inScheme = inScheme
        self.description = description
        self.labels = labels

    def toJSON(self) -> Dict:
        return {
            "id": self.id,
            "skillType": self.skillType,
            "conceptType": self.conceptType,
            "conceptUri": self.conceptUri,
            "reuseLevel": self.reuseLevel,
            "preferredLabel": self.preferredLabel,
            "altLabels": self.altLabels,
            "hiddenLabels": self.hiddenLabels,
            "status": self.status,
            "modifiedDate": self.modifiedDate,
            "scopeNote": self.scopeNote,
            "definition": self.definition,
            "inScheme": self.inScheme,
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
