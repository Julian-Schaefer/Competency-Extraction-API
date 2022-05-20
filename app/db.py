from tokenize import String
from neo4j import GraphDatabase


class GraphDatabaseConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            "bolt://db:7687", auth=("neo4j", "password")
        )

    def close(self):
        self.driver.close()

    def create_competency(
        self, competecyName: String, competencyBody: String
    ) -> String:
        with self.driver.session() as session:
            competency = session.write_transaction(
                self._create_competency_transaction,
                competecyName,
                competencyBody,
            )
            return competency

    @staticmethod
    def _create_competency_transaction(
        tx, competencyName: String, competencyBody: String
    ) -> String:
        result = tx.run(
            "CREATE (c:Competency) "
            "SET c.name = $name "
            "SET c.body = $body "
            "RETURN c.name + ', from node ' + id(c)",
            name=competencyName,
            body=competencyBody,
        )
        return result.single()[0]

    def create_course(self, courseName: String, courseBody: String) -> String:
        with self.driver.session() as session:
            course = session.write_transaction(
                self._create_course_transaction, courseName, courseBody
            )
            return course

    @staticmethod
    def _create_course_transaction(
        tx, courseName: String, courseBody: String
    ) -> String:
        result = tx.run(
            "CREATE (c:Course) "
            "SET c.name = $name "
            "SET c.body = $body "
            "RETURN c.name + ', from node ' + id(c)",
            name=courseName,
            body=courseBody,
        )
        return result.single()[0]
