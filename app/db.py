from neo4j import GraphDatabase


class GraphDatabaseConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver("bolt://db:7687", auth=("neo4j", "password"))

    def close(self):
        self.driver.close()


    def test_connection(self, message):
        with self.driver.session() as session:
            greeting = session.write_transaction(
                self._create_and_return_greeting, message
            )
            return greeting
            

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run(
            "CREATE (a:Greeting) "
            "SET a.message = $message "
            "RETURN a.message + ', from node ' + id(a)",
            message=message,
        )
        return result.single()[0]
