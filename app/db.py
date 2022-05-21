from typing import List, Optional, Dict
from neo4j import GraphDatabase
from neo4j.exceptions import ClientError


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


class GraphDatabaseConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            "bolt://db:7687", auth=("neo4j", "password")
        )

    def close(self):
        self.driver.close()

    def create_competency(
        self, competecyName: str, competencyBody: str
    ) -> str:
        """
        Create competency

        Insert competeny with its name and body into the db

        Parameters:
        competencyName: Competency name as string
        competencyBody: Competency body as string

        Raises: CompetencyInsertionFailed if insertion into DB failed

        Returns:
        Competency name and node as string

        """
        with self.driver.session() as session:
            competency = session.write_transaction(
                self._create_competency_transaction,
                competecyName,
                competencyBody,
            )
            return competency

    @staticmethod
    def _create_competency_transaction(
        tx, competencyName: str, competencyBody: str
    ) -> str:
        query = "CREATE (c:Competency) SET c.name = $name SET c.body = $body RETURN [id(c), c.name, c.body] AS result"
        try:
            result = tx.run(
                query,
                name=competencyName,
                body=competencyBody,
            )
        except ClientError as e:
            raise CompetencyInsertionFailed(f"{query} raised an error: \n {e}")

        result = result.single()["result"]
        competency = {"id": result[0], "name": result[1], "body": result[2]}
        return competency

    def create_course(self, courseName: str, courseBody: str) -> str:
        """
        Create course

        Insert competeny with its name and body into the db

        Parameters:
        courseName: course name as string
        courseBody: course body as string

        Raises: CourseInsertionFailed if insertion into DB failed

        Returns:
        course name and node as string

        """
        with self.driver.session() as session:
            course = session.write_transaction(
                self._create_course_transaction, courseName, courseBody
            )
            return course

    @staticmethod
    def _create_course_transaction(
        tx, courseName: str, courseBody: str
    ) -> str:
        query = "CREATE (c:Course) SET c.name = $name SET c.body = $body RETURN [id(c), c.name, c.body] AS result"
        try:
            result = tx.run(
                query,
                name=courseName,
                body=courseBody,
            )
        except ClientError as e:
            raise CourseInsertionFailed(f"{query} raised an error: \n {e}")

        result = result.single()["result"]
        course = {"id": result[0], "name": result[1], "body": result[2]}
        return course

    def retrieve_all_courses(self) -> List[Optional[Dict]]:
        """
        Retrieve all courses

        Queries all nodes from the DB with the label course

        Raises: RetrieveCoursesFailed if retrieving courses failed

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

        Raises: RetrieveCompetencyFailed if retrieving competencies failed

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

        competencies = [
            {
                "id": c["result"][0],
                "name": c["result"][1],
                "body": c["result"][2],
            }
            for c in result.data()
        ]
        return competencies
