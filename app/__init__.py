from flask import Flask, Response, request, json
from app.db import (
    GraphDatabaseConnection,
    CompetencyInsertionFailed,
    CourseInsertionFailed,
)

app = Flask(__name__)


@app.route("/")
def hello():
    return "<p>Welcome to our API server, you can query courses and competencies here.</p>"


@app.route("/course/<string:course_name>", methods=["POST"])
def create_course(course_name: str):
    if request.headers.get("Content-Type") != "application/json":
        return Response(
            "Content-Type not supported! Expected type application/json",
            status=400,
            mimetype="application/json",
        )

    course_body = json.loads(request.data)["body"]

    db = GraphDatabaseConnection()
    try:
        course = db.create_course(course_name, course_body)
    except CourseInsertionFailed as e:
        return Response(f"error: {e}", status=400, mimetype="application/json")
    db.close()

    return f"<p>Course: {course}</p>"


@app.route("/competency/<string:competency_name>", methods=["POST"])
def create_competency(competency_name):
    if request.headers.get("Content-Type") != "application/json":
        return Response(
            "Content-Type not supported! Expected type application/json",
            status=400,
            mimetype="application/json",
        )

    competency_body = json.loads(request.data)["body"]

    db = GraphDatabaseConnection()
    try:
        competency = db.create_competency(
            competency_name,
            competency_body,
        )
    except CompetencyInsertionFailed as e:
        return Response(f"error: {e}", status=400, mimetype="application/json")
    db.close()

    return f"<p>Competency: {competency}</p>"
