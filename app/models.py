import json
from typing import Dict
from neo4j import Record


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

    @staticmethod
    def fromDatabaseRecord(record: Record):
        competency = Competency(
            id=record["competency"].id,
            skillType=record["competency"]._properties.get("skillType"),
            conceptType=record["competency"]._properties.get("conceptType"),
            conceptUri=record["competency"]._properties.get("conceptUri"),
            reuseLevel=record["competency"]._properties.get("reuseLevel"),
            preferredLabel=record["competency"]._properties.get(
                "preferredLabel"
            ),
            altLabels=record["competency"]._properties.get("altLabels"),
            hiddenLabels=record["competency"]._properties.get("hiddenLabels"),
            status=record["competency"]._properties.get("status"),
            modifiedDate=record["competency"]._properties.get("modifiedDate"),
            scopeNote=record["competency"]._properties.get("scopeNote"),
            definition=record["competency"]._properties.get("definition"),
            inScheme=record["competency"]._properties.get("inScheme"),
            description=record["competency"]._properties.get("description"),
        )

        return competency

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

    @staticmethod
    def fromDatabaseRecord(record: Record):
        course = Course(
            id=record["course"].id,
            description=record["course"]._properties["description"],
        )

        return course

    def toJSON(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
        }
