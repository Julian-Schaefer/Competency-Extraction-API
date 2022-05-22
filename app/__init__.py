from flask import Flask, Response, request, json, jsonify
from app.db import (
    GraphDatabaseConnection,
    CompetencyInsertionFailed,
    CourseInsertionFailed,
    RetrievingCourseFailed,
    RetrievingCompetencyFailed,
    CompetencyAndCourseInsertionFailed,
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
    course_body = json.loads(request.data).get("course_body")

    if not course_body:
        return Response(
            "Body 'course_body' is missing",
            status=400,
            mimetype="application/json",
        )

    db = GraphDatabaseConnection()
    try:
        course = db.create_course(course_name, course_body)
    except CourseInsertionFailed as e:
        return Response(f"error: {e}", status=400, mimetype="application/json")
    db.close()

    return jsonify(course)


@app.route("/courses", methods=["GET", "HEAD"])
def retrieve_courses():
    db = GraphDatabaseConnection()
    try:
        courses = db.retrieve_all_courses()
    except RetrievingCourseFailed as e:
        return Response(f"error: {e}", status=400, mimetype="application/json")
    db.close()

    return jsonify(courses)


@app.route("/competencies", methods=["GET", "HEAD"])
def retrieve_competencies():
    db = GraphDatabaseConnection()
    try:
        competencies = db.retrieve_all_competencies()
    except RetrievingCompetencyFailed as e:
        return Response(f"error: {e}", status=400, mimetype="application/json")
    db.close()

    return jsonify(competencies)


@app.route("/competency/<string:competency_name>", methods=["POST"])
def create_competency(competency_name):
    if request.headers.get("Content-Type") != "application/json":
        return Response(
            "Content-Type not supported! Expected type application/json",
            status=400,
            mimetype="application/json",
        )

    competency_body = json.loads(request.data).get("competency_body")
    if not competency_body:
        return Response(
            "Body 'competency_body' is missing",
            status=400,
            mimetype="application/json",
        )

    db = GraphDatabaseConnection()
    try:
        competency = db.create_competency(
            competency_name,
            competency_body,
        )
    except CompetencyInsertionFailed as e:
        return Response(f"error: {e}", status=400, mimetype="application/json")
    db.close()

    return jsonify(competency)


@app.route("/courseCompetency", methods=["POST"])
def create_competency_course_link():
    if request.headers.get("Content-Type") != "application/json":
        return Response(
            "Content-Type not supported! Expected type application/json",
            status=400,
            mimetype="application/json",
        )
    competency_name = json.loads(request.data).get("competency_name")
    competency_body = json.loads(request.data).get("competency_body")
    course_name = json.loads(request.data).get("course_name")
    course_body = json.loads(request.data).get("course_body")

    if (
        not competency_name
        or not competency_body
        or not course_name
        or not course_body
    ):
        return Response(
            "Body is incomplete, make sure to include 'competency_name', 'competency_body', 'course_name' and 'course_body'",
            status=400,
            mimetype="application/json",
        )

    db = GraphDatabaseConnection()
    try:
        competency_and_course = db.create_competecy_course_connection(
            course_name,
            course_body,
            competency_name,
            competency_body,
        )
    except CompetencyAndCourseInsertionFailed as e:
        return Response(f"error: {e}", status=400, mimetype="application/json")
    db.close()

    return jsonify(competency_and_course)
