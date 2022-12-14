"""
models.py
====================================
Defines models as the essential data structures for the domain of the system.
"""

from typing import Dict, List
from neo4j import Record


class Label:
    """
    Defines the data structure for storing and working with Labels of Competencies.
    Labels are always associated with Competencies.
    """

    def __init__(self, text: str, type: str):
        self.text = text
        self.type = type


class Competency:
    """
    Defines the data structure for storing and working with Competencies.
    Includes all fields defined by the EU-ESCO standard.
    """

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
        labels: List[Label] = None,
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
        """
        Initializes a new instance of a Competency using a Neo4J Database Record.

        :param record: A Neo4J Database Record
        :type record: neo4j.Record

        :return: A new instance of a Competency
        :rtype: Competency
        """
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
        """
        Serializes an existing instance of a Competency into JSON format.

        :return: A Competency serialized as JSON
        :rtype: Dict
        """
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
    """
    Defines the data structure for storing and working with Courses.
    A Course only conists of a description, an id and the type of Competency Extractor that has been used to extract
    Competencies from the description.
    Optionally Courses can be related to multiple Competencies.
    """

    def __init__(
        self,
        id: int,
        description: str,
        extractor: str,
        competencies: List[Competency] = [],
    ):
        self.id = id
        self.description = description
        self.extractor = extractor
        self.competencies = competencies

    @staticmethod
    def fromDatabaseRecord(record: Record):
        """
        Initializes a new instance of a Course using a Neo4J Database Record.

        :param record: A Neo4J Database Record
        :type record: neo4j.Record

        :return: A new instance of a Course
        :rtype: Course
        """
        course = Course(
            id=record["course"].id,
            description=record["course"]._properties["description"],
            extractor=record["course"]._properties["extractor"],
        )

        return course

    def toJSON(self) -> Dict:
        """
        Serializes an existing instance of a Course into JSON format.

        :return: A Course serialized as JSON
        :rtype: Dict
        """
        if self.competencies:
            competencies_json = [
                competency.toJSON() for competency in self.competencies
            ]

            return {
                "id": self.id,
                "description": self.description,
                "extractor": self.extractor,
                "competencies": competencies_json,
            }

        return {
            "id": self.id,
            "description": self.description,
            "extractor": self.extractor,
        }
