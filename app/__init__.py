from flask import Flask, Response, request, json, jsonify
from app.db import (
    GraphDatabaseConnection,
    CourseInsertionFailed,
    RetrievingCourseFailed,
    RetrievingCompetencyFailed,
)
from app.store import Store
from app.competency_extractors.competency_extractor import (
    PaperCompetencyExtractor,
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


@app.route("/course", methods=["GET"])
def retrieve_course():
    competency_id = request.args.get("competencyId")

    db = GraphDatabaseConnection()

    # in case the request body contains a competency_id, filter courses
    if not competency_id:
        try:
            courses = db.retrieve_all_courses()
        except RetrievingCourseFailed as e:
            return Response(
                f"error: {e}", status=400, mimetype="application/json"
            )
    else:
        try:
            courses = db.find_courses_by_competency(int(competency_id))
        except RetrievingCourseFailed as e:
            return Response(
                f"error: {e}", status=400, mimetype="application/json"
            )

    db.close()

    return jsonify(courses)


@app.route("/competency", methods=["GET"])
def retrieve_competency():
    course_id = request.args.get("courseId")

    db = GraphDatabaseConnection()

    if not course_id:
        try:
            competencies = db.retrieve_all_competencies()
        except RetrievingCompetencyFailed as e:
            return Response(
                f"error: {e}", status=400, mimetype="application/json"
            )
    else:
        try:
            competencies = db.find_competencies_by_course(int(course_id))
        except RetrievingCompetencyFailed as e:
            return Response(
                f"error: {e}", status=400, mimetype="application/json"
            )

    db.close()

    return jsonify(competencies)
