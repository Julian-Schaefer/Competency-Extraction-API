from crypt import methods
from telnetlib import STATUS
from flask import Flask
from flask import Response
from app.db import (
    GraphDatabaseConnection,
    CompetencyInsertionFailed,
    CourseInsertionFailed,
)

app = Flask(__name__)


@app.route("/")
def hello():
    return "<p>Welcome to our API server, you can query courses and competencies here.</p>"


@app.route("/course", methods=["POST"])
def course_creation_test():
    db = GraphDatabaseConnection()
    try:
        course = db.create_course("Python 101", "We learn basic Python skills")
    except CourseInsertionFailed as e:
        return Response(f"error: {e}", status=400, mimetype="application/json")
    db.close()

    return f"<p>Course: {course}</p>"


@app.route("/competency", methods=["POST"])
def competency_creation_test():
    db = GraphDatabaseConnection()
    try:
        competency = db.create_competency(
            "Basic Python skills",
            "data structures, string manipulation and OOP",
        )
    except CompetencyInsertionFailed as e:
        return Response(f"error: {e}", status=400, mimetype="application/json")
    db.close()

    return f"<p>Competency: {competency}</p>"
