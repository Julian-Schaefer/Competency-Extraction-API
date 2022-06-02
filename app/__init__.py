from flask import Flask, Response, request, json, jsonify
from app.db import (
    GraphDatabaseConnection,
    CompetencyInsertionFailed,
    CourseInsertionFailed,
    RetrievingCourseFailed,
    RetrievingCompetencyFailed,
    CompetencyAndCourseInsertionFailed,
)
from app.store import Store
from app.competency_extractors.competency_extractor import (
    PaperCompetencyExtractor,
    DummyExtractor,
)


app = Flask(__name__)


@app.route("/")
def hello():
    return "<p>Welcome to our API server, you can query courses and competencies here.</p>"


@app.route("/initialize", methods=["POST"])
def initialize():
    store = Store()
    store.initialize()
    return "Database and Store have been initialized successfully!"


@app.route("/course", methods=["POST"])
def create_course():
    if request.headers.get("Content-Type") != "application/json":
        return Response(
            "Content-Type not supported! Expected type application/json",
            status=400,
            mimetype="application/json",
        )
    course_description = json.loads(request.data).get("courseDescription")

    if not course_description:
        return Response(
            "Body 'course_description' is missing",
            status=400,
            mimetype="application/json",
        )

    competencyExtractor = PaperCompetencyExtractor()
    db = GraphDatabaseConnection()
    try:
        associated_competencies = competencyExtractor.extract_competencies(
            course_description
        )
        associated_competencies_ids = [
            competency[0] for competency in associated_competencies
        ]

        db.create_course(course_description, associated_competencies_ids)
    except CourseInsertionFailed as e:
        return Response(f"error: {e}", status=400, mimetype="application/json")
    db.close()

    return jsonify(associated_competencies)


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


@app.route("/course/<string:course_name>/extract", methods=["POST"])
def create_course_with_extraction(course_name: str):
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
    extractor = DummyExtractor()
    competencies = extractor.extract_competencies(course_body)

    created_links = []

    for competency in competencies:
        competency_name = competency.get("name")
        competency_body = competency.get("body")

        try:
            competency_and_course = db.create_competecy_course_connection(
                course_name,
                course_body,
                competency_name,
                competency_body,
            )
        except CompetencyAndCourseInsertionFailed:
            continue
        created_links.append(competency_and_course)

    db.close()

    return jsonify(created_links)
