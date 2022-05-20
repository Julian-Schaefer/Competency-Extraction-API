from flask import Flask
from app.db import GraphDatabaseConnection

app = Flask(__name__)


# @app.route("/")
# def course_creation_test():
#     db = GraphDatabaseConnection()
#     course = db.create_course("Python 101", "We learn basic Python skills")
#     db.close()

#     return f"<p>Course: {course}</p>"


@app.route("/")
def competency_creation_test():
    db = GraphDatabaseConnection()
    competency = db.create_competency(
        "Basic Python skills", "data structures, string manipulation and OOP"
    )
    db.close()

    return f"<p>Course: {competency}</p>"
