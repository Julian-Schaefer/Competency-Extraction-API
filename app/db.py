from typing import List, Optional, Dict
from xmlrpc.client import Boolean
from neo4j import GraphDatabase
from neo4j.exceptions import ClientError
import os
from app.models import Competency, Course


class CompetencyInsertionFailed(Exception):
    """Raised when competency couldn't be inserted into the DB"""

    pass


class CourseInsertionFailed(Exception):
    """Raised when course couldn't be inserted into the DB"""

    pass


class RetrievingCourseFailed(Exception):
    """Raised when course(s) couldn't be retrieved"""

    pass


class RetrievingCompetencyFailed(Exception):
    """Raised when competency(ies) couldn't be retrieved"""

    pass


class RetrievingLabelFailed(Exception):
    """Raised when label/s couldn't be retrieved"""

    pass


class GraphDatabaseConnection:
    def __init__(self):
        db_uri = os.environ.get("DB_URI")
        self.driver = GraphDatabase.driver(db_uri, auth=("neo4j", "password"))

    def close(self):
        self.driver.close()

    def create_competency(self, competency: Competency) -> None:
        """
        Create competency

        Insert competeny with its properties and labels into the db

        Parameters:
            competency: Competency with Properties and Labels

        Raises: CompetencyInsertionFailed if insertion into DB failed

        """
        uri = competency.conceptUri
        if not self.retrieve_competency_by_uri(uri):
            self.create_competencies([competency])

    def create_competencies(self, competencies: List[Competency]) -> None:
        """
        Create competencies

        Insert competencies with their properties and labels into the db

        Parameters:
            competencies: List of Competencies with Properties and Labels

        Raises: CompetencyInsertionFailed if insertion into DB failed

        """
        with self.driver.session() as session:
            session.write_transaction(self._create_competencies, competencies)

    @staticmethod
    def _create_competencies(tx, competencies: List[Competency]):
        for competency in competencies:
            create_competency_query = (
                "CREATE (com:Competency {conceptType:$conceptType, conceptUri:$conceptUri, skillType:$skillType, "
                "reuseLevel:$reuseLevel, preferredLabel:$preferredLabel, altLabels:$altLabels, hiddenLabels:$hiddenLabels, status:$status, "
                "modifiedDate:$modifiedDate, scopeNote:$scopeNote, definition:$definition, inScheme:$inScheme, description:$description}) RETURN id(com) AS id"
            )

            try:
                result = tx.run(
                    create_competency_query,
                    conceptType=competency.conceptType,
                    conceptUri=competency.conceptUri,
                    skillType=competency.skillType,
                    reuseLevel=competency.reuseLevel,
                    preferredLabel=competency.preferredLabel,
                    altLabels=competency.altLabels,
                    hiddenLabels=competency.hiddenLabels,
                    status=competency.status,
                    modifiedDate=competency.modifiedDate,
                    scopeNote=competency.scopeNote,
                    definition=competency.definition,
                    inScheme=competency.inScheme,
                    description=competency.description,
                )

                if not result:
                    raise CompetencyInsertionFailed(
                        "Inserting Competency did not return result."
                    )

                result = result.single()
                competencyId = result["id"]
            except ClientError as e:
                raise CompetencyInsertionFailed(
                    f"{create_competency_query} raised an error: \n {e}"
                )

            create_label_query = "CREATE (lab:Label {text:$text, type:$type}) RETURN id(lab) AS id"
            create_relation_query = "MATCH (com:Competency) WHERE id(com)=$competencyId MATCH (lab:Label) WHERE id(lab)=$labelId CREATE (com)-[r:IDENTIFIED_BY]->(lab)"

            for label in competency.labels:
                try:
                    result = tx.run(
                        create_label_query,
                        text=label.text,
                        type=label.type,
                    )

                    if not result:
                        raise CompetencyInsertionFailed(
                            "Inserting Label did not return result."
                        )

                    result = result.single()
                    labelId = result["id"]
                except ClientError as e:
                    raise CompetencyInsertionFailed(
                        f"{create_label_query} raised an error: \n {e}"
                    )

                try:
                    tx.run(
                        create_relation_query,
                        competencyId=competencyId,
                        labelId=labelId,
                    )
                except ClientError as e:
                    raise CompetencyInsertionFailed(
                        f"{create_relation_query} raised an error: \n {e}"
                    )

    def create_course(
        self, course_description: str, associated_competencies
    ) -> Course:
        """
        Create course

        Insert Course with its description and associated competencies

        Parameters:
            course_description: course description as string
            associated_competencies: associated competencies for this course description

        Raises: CourseInsertionFailed if insertion into DB failed

        """
        associated_competencies_ids = [
            competency.id for competency in associated_competencies
        ]

        associated_competencies_ids = list(set(associated_competencies_ids))

        with self.driver.session() as session:
            course = session.write_transaction(
                self._create_course_transaction,
                course_description,
                associated_competencies_ids,
            )
            return course

    @staticmethod
    def _create_course_transaction(
        tx, course_description: str, associated_competencies_ids
    ) -> Course:
        create_course_query = "CREATE (c:Course) SET c.description = $description RETURN id(c) AS id"
        try:
            result = tx.run(
                create_course_query, description=course_description
            )
            course_id = result.single()["id"]
        except ClientError as e:
            raise CourseInsertionFailed(
                f"{create_course_query} raised an error: \n {e}"
            )

        create_relation_query = "MATCH (cou:Course) WHERE id(cou)=$courseId MATCH (com:Competency) WHERE id(com)=$competencyId CREATE (cou)-[r:MATCHES]->(com)"

        for competency_id in associated_competencies_ids:
            try:
                tx.run(
                    create_relation_query,
                    courseId=course_id,
                    competencyId=competency_id,
                )
            except ClientError as e:
                raise CompetencyInsertionFailed(
                    f"{create_relation_query} raised an error: \n {e}"
                )

        return Course(id=course_id, description=course_description)

    def retrieve_all_courses(self) -> List[Course]:
        """
        Retrieve all courses

        Queries all nodes from the DB with the label course

        Raises: RetrievingCourseFailed if retrieving courses failed

        Returns:
        List of courses as dict

        """
        with self.driver.session() as session:
            course = session.write_transaction(self._retrieve_all_courses)
            return course

    @staticmethod
    def _retrieve_all_courses(tx) -> List[Course]:
        query = "MATCH (c:Course) RETURN c AS result"
        try:
            result = tx.run(
                query,
            )
        except ClientError as e:
            raise RetrievingCourseFailed(f"{query} raised an error: \n {e}")

        courses = [
            Course(
                id=c["result"].id,
                description=c["result"]._properties["description"],
            )
            for c in result
        ]

        return courses

    def retrieve_all_competencies(self) -> List[Competency]:
        """
        Retrieve all competencies

        Queries all nodes from the DB with the label competency

        Raises: RetrievingCompetencyFailed if retrieving competencies failed

        Returns:
        List of competencies as dict

        """
        with self.driver.session() as session:
            competencies = session.write_transaction(
                self._retrieve_all_competencies
            )
            return competencies

    @staticmethod
    def _retrieve_all_competencies(tx) -> List[Competency]:
        query = "MATCH (c:Competency) RETURN c AS competency"
        try:
            result = tx.run(
                query,
            )
        except ClientError as e:
            raise RetrievingCompetencyFailed(
                f"{query} raised an error: \n {e}"
            )

        if not result:
            return None

        competencies = [
            Competency(
                id=record["competency"].id,
                skillType=record["competency"]._properties.get("skillType"),
                conceptType=record["competency"]._properties.get(
                    "conceptType"
                ),
                conceptUri=record["competency"]._properties.get("conceptUri"),
                reuseLevel=record["competency"]._properties.get("reuseLevel"),
                preferredLabel=record["competency"]._properties.get(
                    "preferredLabel"
                ),
                altLabels=record["competency"]._properties.get("altLabels"),
                hiddenLabels=record["competency"]._properties.get(
                    "hiddenLabels"
                ),
                status=record["competency"]._properties.get("status"),
                modifiedDate=record["competency"]._properties.get(
                    "modifiedDate"
                ),
                scopeNote=record["competency"]._properties.get("scopeNote"),
                definition=record["competency"]._properties.get("definition"),
                inScheme=record["competency"]._properties.get("inScheme"),
                description=record["competency"]._properties.get(
                    "description"
                ),
            )
            for record in result
        ]
        return competencies

    def find_label_by_term(self, term) -> Boolean:
        """Check if Label exists by term

        Retrieves all labels containing this term and returns true, if there
        is more than 1 label containing that term. Returns false otherwise.

        Parameters:
            term: a single word as string

        Raises:
            RetrievingLabelFailed if communication with the database goes wrong

        Returns:
            If the term exists in a label as boolean
        """
        with self.driver.session() as session:
            is_found = session.write_transaction(
                self._find_label_by_term, term
            )
            return is_found

    @staticmethod
    def _find_label_by_term(tx, term) -> Boolean:
        query = "MATCH (lab:Label) where lab.text CONTAINS $term RETURN lab AS label"

        try:
            result = tx.run(query, term=term)

            if not result:
                return None

            labels = [record["label"]._properties for record in result]
            count = len(labels)
            return count > 0
        except Exception as e:
            raise RetrievingLabelFailed(f"{query} raised an error: \n {e}")

    def find_competency_by_sequence(self, sequence) -> List[Competency]:
        """Find competency by Sequence

        Find all competencies by matching their labels to the complete sequence that
        has been provided.

        Parameters:
            sequence: sequence of words as string

        Raises:
            RetrievingCompetencyFailed if communication with the database goes wrong

        Returns:
            Matching competencies as dict
        """
        with self.driver.session() as session:
            competencies = session.write_transaction(
                self._find_competency_by_sequence, sequence
            )
            return competencies

    @staticmethod
    def _find_competency_by_sequence(tx, sequence) -> List[Competency]:
        query = "MATCH (lab:Label)<-[:IDENTIFIED_BY]-(com:Competency) where lab.text=$sequence RETURN com AS competency"

        try:
            result = tx.run(query, sequence=sequence)

            if not result:
                return None

            competencies = [
                Competency(
                    id=record["competency"].id,
                    skillType=record["competency"]._properties.get(
                        "skillType"
                    ),
                    conceptType=record["competency"]._properties.get(
                        "conceptType"
                    ),
                    conceptUri=record["competency"]._properties.get(
                        "conceptUri"
                    ),
                    reuseLevel=record["competency"]._properties.get(
                        "reuseLevel"
                    ),
                    preferredLabel=record["competency"]._properties.get(
                        "preferredLabel"
                    ),
                    altLabels=record["competency"]._properties.get(
                        "altLabels"
                    ),
                    hiddenLabels=record["competency"]._properties.get(
                        "hiddenLabels"
                    ),
                    status=record["competency"]._properties.get("status"),
                    modifiedDate=record["competency"]._properties.get(
                        "modifiedDate"
                    ),
                    scopeNote=record["competency"]._properties.get(
                        "scopeNote"
                    ),
                    definition=record["competency"]._properties.get(
                        "definition"
                    ),
                    inScheme=record["competency"]._properties.get("inScheme"),
                    description=record["competency"]._properties.get(
                        "description"
                    ),
                )
                for record in result
            ]
            return competencies
        except Exception as e:
            raise RetrievingCompetencyFailed(
                f"{query} raised an error: \n {e}"
            )

    @staticmethod
    def _find_courses_by_competency(tx, competency_id: int) -> List[Course]:
        query = "MATCH (com:Competency)<-[:MATCHES]-(cou:Course) WHERE id(com)=$id RETURN cou AS course"

        try:
            result = tx.run(query, id=competency_id)

            if not result:
                return None

            courses = [
                Course(
                    id=record["course"].id,
                    description=record["course"]._properties["description"],
                )
                for record in result
            ]
            return courses
        except Exception as e:
            raise RetrievingCourseFailed(f"{query} raised an error: \n {e}")

    def find_courses_by_competency(self, competency_id: int) -> List[Course]:
        """Find competencies by course

        Find courses by matching their competency provided by it's ID.

        Parameters:
            competency_id: id of the competency as integer

        Raises:
            RetrievingCourseFailed if communication with the database goes wrong

        Returns:
            Matching courses as list of dicts
        """
        with self.driver.session() as session:
            courses = session.write_transaction(
                self._find_courses_by_competency, competency_id
            )
            return courses

    @staticmethod
    def _find_courses_by_text_query(
        tx, text_search_query: str
    ) -> List[Course]:
        query = "MATCH (cou:Course) where cou.description CONTAINS $text_search_query RETURN cou AS course"

        try:
            result = tx.run(query, text_search_query=text_search_query)

            if not result:
                return None

            courses = [
                Course(
                    id=record["course"].id,
                    description=record["course"]._properties["description"],
                )
                for record in result
            ]
            return courses
        except Exception as e:
            raise RetrievingCourseFailed(f"{query} raised an error: \n {e}")

    def find_courses_by_text_query(
        self, text_search_query: str
    ) -> List[Course]:
        with self.driver.session() as session:
            courses = session.write_transaction(
                self._find_courses_by_text_query, text_search_query
            )
            return courses

    @staticmethod
    def _find_competencies_by_course(tx, course_id: int) -> Dict:
        query = "MATCH (com:Competency)<-[:MATCHES]-(cou:Course) where id(cou)=$id RETURN com AS competency"

        try:
            result = tx.run(query, id=course_id)

            if not result:
                return None

            competencies = [
                Competency(
                    id=record["competency"].id,
                    skillType=record["competency"]._properties.get(
                        "skillType"
                    ),
                    conceptType=record["competency"]._properties.get(
                        "conceptType"
                    ),
                    conceptUri=record["competency"]._properties.get(
                        "conceptUri"
                    ),
                    reuseLevel=record["competency"]._properties.get(
                        "reuseLevel"
                    ),
                    preferredLabel=record["competency"]._properties.get(
                        "preferredLabel"
                    ),
                    altLabels=record["competency"]._properties.get(
                        "altLabels"
                    ),
                    hiddenLabels=record["competency"]._properties.get(
                        "hiddenLabels"
                    ),
                    status=record["competency"]._properties.get("status"),
                    modifiedDate=record["competency"]._properties.get(
                        "modifiedDate"
                    ),
                    scopeNote=record["competency"]._properties.get(
                        "scopeNote"
                    ),
                    definition=record["competency"]._properties.get(
                        "definition"
                    ),
                    inScheme=record["competency"]._properties.get("inScheme"),
                    description=record["competency"]._properties.get(
                        "description"
                    ),
                )
                for record in result
            ]

            return competencies
        except Exception as e:
            raise RetrievingCompetencyFailed(
                f"{query} raised an error: \n {e}"
            )

    def find_competencies_by_course(self, course_id: int) -> List[Dict]:
        """Find courses by competency

        Find competencies by matching the course that they are connected to provided by it's ID.

        Parameters:
            course_id: id of the course as integer

        Raises:
            RetrievingCompetencyFailed if communication with the database goes wrong

        Returns:
            Matching competencies as list of dicts
        """
        with self.driver.session() as session:
            competencies = session.write_transaction(
                self._find_competencies_by_course, course_id
            )
            return competencies
