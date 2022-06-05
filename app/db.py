from typing import List, Optional, Dict
from xmlrpc.client import Boolean
from neo4j import GraphDatabase
from neo4j.exceptions import ClientError
import os


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


class CompetencyAndCourseInsertionFailed(Exception):
    """Raised when relationship between competency and course could not be created"""

    pass


class GraphDatabaseConnection:
    def __init__(self):
        db_uri = os.environ.get("DB_URI")
        self.driver = GraphDatabase.driver(db_uri, auth=("neo4j", "password"))

    def close(self):
        self.driver.close()

    def create_competency(self, competency) -> None:
        """
        Create competency

        Insert competeny with its properties and labels into the db

        Parameters:
            competency: Competency with Properties and Labels

        Raises: CompetencyInsertionFailed if insertion into DB failed

        """
        uri = competency["conceptUri"]
        if not self.retrieve_competency_by_uri(uri):
            self.create_competencies([competency])

    def create_competencies(self, competencies) -> None:
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
    def _create_competencies(tx, competencies):
        for competency in competencies:
            create_competency_query = "CREATE (com:Competency {conceptType:$conceptType, conceptUri:$conceptUri, competencyType:$competencyType, description:$description}) RETURN id(com) AS id"

            try:
                result = tx.run(
                    create_competency_query,
                    conceptType=competency["conceptType"],
                    conceptUri=competency["conceptUri"],
                    competencyType=competency["competencyType"],
                    description=competency["description"],
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

            for label in competency["labels"]:
                try:
                    result = tx.run(
                        create_label_query,
                        text=label["text"],
                        type=label["type"],
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
    ) -> str:
        """
        Create course

        Insert Course with its description and associated competencies

        Parameters:
            course_description: course description as string
            associated_competencies: associated competencies for this course description

        Raises: CourseInsertionFailed if insertion into DB failed

        """
        associated_competencies_ids = [
            competency[0] for competency in associated_competencies
        ]

        associated_competencies_ids = list(set(associated_competencies_ids))

        with self.driver.session() as session:
            session.write_transaction(
                self._create_course_transaction,
                course_description,
                associated_competencies_ids,
            )

    @staticmethod
    def _create_course_transaction(
        tx, course_description: str, associated_competencies_ids
    ) -> str:
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

    def retrieve_all_courses(self) -> List[Optional[Dict]]:
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
    def _retrieve_all_courses(tx) -> List[Optional[Dict]]:
        query = "MATCH (c:Course) RETURN [id(c), c.name, c.body] AS result"
        try:
            result = tx.run(
                query,
            )
        except ClientError as e:
            raise RetrievingCourseFailed(f"{query} raised an error: \n {e}")

        if not result.data():
            return None

        courses = [
            {
                "id": c["result"][0],
                "name": c["result"][1],
                "body": c["result"][2],
            }
            for c in result.data()
        ]
        return courses

    def retrieve_all_competencies(self) -> List[Optional[Dict]]:
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
    def _retrieve_all_competencies(tx) -> List[Optional[Dict]]:
        query = "MATCH (c:Competency) RETURN [id(c), c.name, c.body] AS result"
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
            {
                "id": c["result"][0],
                "name": c["result"][1],
                "body": c["result"][2],
            }
            for c in result.data()
        ]
        return competencies

    def retrieve_competency_by_uri(self, uri) -> Optional[Dict]:
        """
        Retrieve competency by name

        Query nodes with label Competency that have name competencyName

        Parameters:
            competencyName: competency name as string

        Raises:
            RetrievingCompetencyFailed if retrieving competency failed

        Returns:
            Competency as dict or None
        """
        with self.driver.session() as session:
            competency = session.write_transaction(
                self._retrieve_competency_by_uri, uri
            )
            return competency

    @staticmethod
    def _retrieve_competency_by_uri(tx, uri) -> Optional[Dict]:
        query = "MATCH (com:Competency) WHERE com.conceptUri=$uri RETURN id(com) AS id"
        try:
            result = tx.run(query, uri=uri)
        except ClientError as e:
            raise RetrievingCompetencyFailed(
                f"{query} raised an error: \n {e}"
            )
        if not result:
            return None
        result = result.single()
        if not result:
            return None
        return result["id"]

    @staticmethod
    def _retrieve_course_by_name(tx, courseName) -> Optional[Dict]:
        query = "MATCH (c:Course) WHERE c.name=$name RETURN [id(c), c.name, c.body] AS result"
        try:
            result = tx.run(query, name=courseName)
        except ClientError as e:
            raise RetrievingCourseFailed(f"{query} raised an error: \n {e}")
        if not result:
            return None
        result = result.single()
        if not result:
            return None
        result = result["result"]
        course = {"id": result[0], "name": result[1], "body": result[2]}

        return course

    def retrieve_course_by_name(self, courseName) -> Optional[Dict]:
        """
        Retrieve course by name

        Query nodes with label Course that have name courseName

        Parameters:
            courseName: course name as string

        Raises:
            RetrievingCourseFailed if retrieving course failed

        Returns:
            Course as dict or None
        """
        with self.driver.session() as session:
            competency = session.write_transaction(
                self._retrieve_course_by_name, courseName
            )
            return competency

    @staticmethod
    def _insert_course_with_nonexisting_competency(
        tx, competencyName, competencyBody, courseName, courseBody
    ) -> Dict:
        query = "CREATE (cou:Course {name:$courseName, body:$courseBody})-[r:HAS]->(com:Competency {name:$competencyName, body:$competencyBody}) RETURN [id(cou), cou.name, cou.body, id(com), com.name, com.body] AS result"
        try:
            result = tx.run(
                query,
                competencyName=competencyName,
                competencyBody=competencyBody,
                courseName=courseName,
                courseBody=courseBody,
            )
        except ClientError as e:
            raise CompetencyAndCourseInsertionFailed(
                f"{query} raised an error: \n {e}"
            )

        if not result:
            return None
        result = result.single()
        if not result:
            return None
        result = result["result"]
        course_and_competency = {
            "course_id": result[0],
            "course_name": result[1],
            "course_body": result[2],
            "competency_id": result[3],
            "competency_name": result[4],
            "competency_body": result[5],
        }
        return course_and_competency

    def insert_course_with_nonexisting_competency(
        self, competencyName, competencyBody, courseName, courseBody
    ) -> Dict:
        """
        Insert course with nonexisting competency

        Create a new course and HAS relationship to a new competency

        Parameters:
            competencyName: competency name as string
            competencyBody: competency body as string
            courseName: course name as string
            courseBody: course body as string

        Raises:
            CompetencyAndCourseInsertionFailed if creating failed

        Returns:
            Course and competency as dict
        """
        with self.driver.session() as session:
            competency_and_course = session.write_transaction(
                self._insert_course_with_nonexisting_competency,
                competencyName,
                competencyBody,
                courseName,
                courseBody,
            )
            return competency_and_course

    @staticmethod
    def _insert_course_with_existing_competency(
        tx, competencyId, courseName, courseBody
    ) -> Dict:
        query = "MATCH (com:Competency) WHERE id(com)=$competencyId CREATE (cou:Course {name:$courseName, body:$courseBody})-[r:HAS]->(com) RETURN [id(cou), cou.name, cou.body, id(com), com.name, com.body] AS result"
        try:
            result = tx.run(
                query,
                competencyId=competencyId,
                courseName=courseName,
                courseBody=courseBody,
            )
        except ClientError as e:
            raise CompetencyAndCourseInsertionFailed(
                f"{query} raised an error: \n {e}"
            )
        if not result:
            return None
        result = result.single()
        if not result:
            return None
        result = result["result"]
        course_and_competency = {
            "course_id": result[0],
            "course_name": result[1],
            "course_body": result[2],
            "competency_id": result[3],
            "competency_name": result[4],
            "competency_body": result[5],
        }
        return course_and_competency

    def insert_course_with_existing_competency(
        self, competencyId, courseName, courseBody
    ) -> Dict:
        """Insert course with existing competency

        Create a new course and HAS relationship to an existing competency

        Parameters:
            competencyId: id of the existing competency
            courseName: course name as string
            courseBody: course body as string

        Raises:
            CompetencyAndCourseInsertionFailed if creating failed

        Returns:
            Course and competency as dict
        """
        with self.driver.session() as session:
            competency_and_course = session.write_transaction(
                self._insert_course_with_existing_competency,
                competencyId,
                courseName,
                courseBody,
            )
            return competency_and_course

    @staticmethod
    def _insert_competency_with_existing_course(
        tx, competencyName, competencyBody, courseId
    ) -> Dict:
        query = "MATCH (cou:Course) WHERE id(cou)=$courseId CREATE (cou)-[r:HAS]->(com:Competency {name:$competencyName, body:$competencyBody}) RETURN [id(cou), cou.name, cou.body, id(com), com.name, com.body] AS result"
        try:
            result = tx.run(
                query,
                courseId=courseId,
                competencyName=competencyName,
                competencyBody=competencyBody,
            )
        except ClientError as e:
            raise CompetencyAndCourseInsertionFailed(
                f"{query} raised an error: \n {e}"
            )
        if not result:
            return None
        result = result.single()
        if not result:
            return None
        result = result["result"]
        course_and_competency = {
            "course_id": result[0],
            "course_name": result[1],
            "course_body": result[2],
            "competency_id": result[3],
            "competency_name": result[4],
            "competency_body": result[5],
        }
        return course_and_competency

    def insert_competency_with_existing_course(
        self, competencyName, competencyBody, courseId
    ) -> Dict:
        """Insert competency with existing course

        Create a new competency and HAS relationship from an existing course

        Parameters:
            competencyName: competency name as string
            competencyBody: competency body as string
            courseId: id of the existing course

        Raises:
            CompetencyAndCourseInsertionFailed if creating failed

        Returns:
            Course and competency as dict
        """
        with self.driver.session() as session:
            competency_and_course = session.write_transaction(
                self._insert_competency_with_existing_course,
                competencyName,
                competencyBody,
                courseId,
            )
            return competency_and_course

    @staticmethod
    def _retrieve_existing_relationship(tx, competencyId, courseId) -> Dict:
        query = "MATCH (cou:Course), (com: Competency) WHERE id(cou)=$courseId AND id(com)=$competencyId AND (cou)-[:HAS]->(com) RETURN [id(cou), cou.name, cou.body, id(com), com.name, com.body] AS result"
        try:
            result = tx.run(
                query,
                competencyId=competencyId,
                courseId=courseId,
            )
        except ClientError as e:
            raise CompetencyAndCourseInsertionFailed(
                f"{query} raised an error: \n {e}"
            )

        if not result:
            return None
        result = result.single()
        if not result:
            return None
        result = result["result"]
        course_and_competency = {
            "course_id": result[0],
            "course_name": result[1],
            "course_body": result[2],
            "competency_id": result[3],
            "competency_name": result[4],
            "competency_body": result[5],
        }
        return course_and_competency

    def retrieve_existing_relationship(
        self, courseId, competencyId
    ) -> List[Optional[Dict]]:
        """Retrieve existing relationship

        Retrieve HAS relationship between given competency and course

        Parameters:
            competencyId: Id of the existing competency
            courseId: id of the existing course

        Raises:
            CompetencyAndCourseInsertionFailed if creating failed

        Returns:
            Course and competency as dict
        """
        with self.driver.session() as session:
            relationship = session.write_transaction(
                self._retrieve_existing_relationship,
                competencyId,
                courseId,
            )
            return relationship

    @staticmethod
    def _insert_relationship_for_existing(tx, competencyId, courseId) -> Dict:
        query = "MATCH (cou:Course) WHERE id(cou)=$courseId MATCH (com:Competency) WHERE id(com)=$competencyId CREATE (cou)-[r:HAS]->(com) RETURN [id(cou), cou.name, cou.body, id(com), com.name, com.body] AS result"
        try:
            result = tx.run(
                query,
                competencyId=competencyId,
                courseId=courseId,
            )
        except ClientError as e:
            raise CompetencyAndCourseInsertionFailed(
                f"{query} raised an error: \n {e}"
            )

        if not result:
            return None
        result = result.single()
        if not result:
            return None
        result = result["result"]
        course_and_competency = {
            "course_id": result[0],
            "course_name": result[1],
            "course_body": result[2],
            "competency_id": result[3],
            "competency_name": result[4],
            "competency_body": result[5],
        }
        return course_and_competency

    def insert_relationship_for_existing(self, competencyId, courseId) -> Dict:
        """Insert relationship for existing

        Create a new HAS relationship between existing course and competency

        Parameters:
            competencyId: Id of existing competency
            courseId: id of the existing course

        Raises:
            CompetencyAndCourseInsertionFailed if creating failed

        Returns:
            Course and competency as dict
        """
        if self.retrieve_existing_relationship(courseId, competencyId):
            raise CompetencyAndCourseInsertionFailed(
                f"Competency {competencyId} and course {courseId} already have a relationship."
            )
        with self.driver.session() as session:
            competency_and_course = session.write_transaction(
                self._insert_relationship_for_existing,
                competencyId,
                courseId,
            )
            return competency_and_course

    def create_competecy_course_connection(
        self, courseName, courseBody, competencyName, competecyBody
    ) -> Dict:
        """Create competency course connection

        Create a new HAS relationship between course and competency avoiding duplicates

        Parameters:
            competencyName: competency name as string
            competencyBody: competency body as string
            courseName: course name as string
            courseBody: course body as string

        Raises:
            CompetencyAndCourseInsertionFailed if creating failed

        Returns:
            Course and competency as dict
        """
        existing_competency = self.retrieve_competency_by_name(competencyName)
        existing_course = self.retrieve_course_by_name(courseName)

        if existing_course and existing_competency:
            return self.insert_relationship_for_existing(
                existing_competency.get("id"), existing_course.get("id")
            )

        if existing_course and not existing_competency:
            return self.insert_competency_with_existing_course(
                competencyName, competecyBody, existing_course.get("id")
            )
        if not existing_course and existing_competency:
            return self.insert_course_with_existing_competency(
                existing_competency["id"], courseName, courseBody
            )

        # competency and course both don't exist yet
        return self.insert_course_with_nonexisting_competency(
            competencyName, competecyBody, courseName, courseBody
        )

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

    def find_competency_by_sequence(self, sequence) -> Dict:
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
    def _find_competency_by_sequence(tx, sequence) -> Dict:
        query = "MATCH (lab:Label)<-[:IDENTIFIED_BY]-(com:Competency) where lab.text=$sequence RETURN com AS competency"

        try:
            result = tx.run(query, sequence=sequence)

            if not result:
                return None

            competencies = [
                (record["competency"].id, record["competency"]._properties)
                for record in result
            ]
            return competencies
        except Exception as e:
            raise RetrievingCompetencyFailed(
                f"{query} raised an error: \n {e}"
            )

    @staticmethod
    def _find_courses_by_competency(tx, competency_id: int) -> Dict:
        query = "MATCH (com:Competency)<-[:HAS]-(cou:Course) where id(com)=$id RETURN cou AS course"

        try:
            result = tx.run(query, id=competency_id)

            if not result:
                return None

            courses = [record["course"]._properties for record in result]
            return courses
        except Exception as e:
            raise RetrievingCourseFailed(f"{query} raised an error: \n {e}")

    def find_courses_by_competency(self, competency_id: int) -> List[Dict]:
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
    def _find_competencies_by_course(tx, course_id: int) -> Dict:
        query = "MATCH (com:Competency)<-[:HAS]-(cou:Course) where id(cou)=$id RETURN com AS competency"

        try:
            result = tx.run(query, id=course_id)

            if not result:
                return None

            competencies = [
                record["competency"]._properties for record in result
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
