from neo4j import GraphDatabase
from neo4j.exceptions import ClientError


class CompetencyInsertionFailed(Exception):
    """Raised when competency couldn't be inserted into the DB"""

    pass


class CourseInsertionFailed(Exception):
    """Raised when course couldn't be inserted into the DB"""

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
        query = "CREATE (c:Competency) SET c.name = $name SET c.body = $body RETURN c.name + ', from node ' + id(c)"
        try:
            result = tx.run(
                query,
                name=competencyName,
                body=competencyBody,
            )
        except ClientError as e:
            raise CompetencyInsertionFailed(f"{query} raised an error: \n {e}")
        return result.single()[0]

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
        query = "CREATE (c:Course) SET c.name = $name SET c.body = $body RETURN c.name + ', from node ' + id(c)"
        try:
            result = tx.run(
                query,
                name=courseName,
                body=courseBody,
            )
        except ClientError as e:
            raise CourseInsertionFailed(f"{query} raised an error: \n {e}")
        return result.single()[0]
