from flask import Flask
from app.db import GraphDatabaseConnection

app = Flask(__name__)


@app.route("/")
def hello_world():
    db = GraphDatabaseConnection()
    greeting = db.test_connection("hello, world I'm connected")
    db.close()

    return f"<p>{greeting}</p>"
