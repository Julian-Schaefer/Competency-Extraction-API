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
import xml.etree.ElementTree as ET
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__, static_folder="../docs", static_url_path="/docs")


SWAGGER_URL = "/api/docs"  # URL for exposing Swagger UI (without trailing '/')
API_DEFINITION_FILE = "../../docs/api_spec_swagger.yml"  # Our API Definition

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_DEFINITION_FILE,
)

app.register_blueprint(swaggerui_blueprint)


@app.route("/")
def hello():
    return "<h1>Welcome!</h1><p>Welcome to our API server, you can query courses and competencies here.</p>"


@app.route("/initialize", methods=["POST"])
def initialize():
    store = Store()
    store.initialize()
    return "Database and Store have been initialized successfully!"


@app.route("/course", methods=["POST"])
def create_course():
    if request.headers.get("Content-Type") == "application/json":
        course_description = json.loads(request.data).get("courseDescription")

        if not course_description:
            return Response(
                "Body 'course_description' is missing",
                status=400,
                mimetype="application/json",
            )

        competencyExtractor = PaperCompetencyExtractor()

        associated_competencies = competencyExtractor.extract_competencies(
            course_description
        )

        db = GraphDatabaseConnection()
        try:
            course = db.create_course(
                course_description, associated_competencies
            )
        except CourseInsertionFailed as e:
            return Response(
                f"error: {e}", status=400, mimetype="application/json"
            )
        db.close()

        return jsonify(
            {
                "course": course.toJSON(),
                "competencies": [
                    competency.toJSON()
                    for competency in associated_competencies
                ],
            }
        )
    elif request.headers.get("Content-Type").startswith("multipart/form-data"):
        try:
            courses_file = request.files["courses"]

            courses_xml = ET.parse(
                courses_file.stream, parser=ET.XMLParser(encoding="utf-8")
            )
            courses = courses_xml.findall(".//COURSE")
        except:
            return Response(
                "An error occured while reading the file. Please make sure to upload a correctly formatted XML file named as 'courses'.",
                status=400,
                mimetype="application/json",
            )

        if len(courses) > 0:
            competencyExtractor = PaperCompetencyExtractor()
            db = GraphDatabaseConnection()

            for course in courses:
                course_description = course.find("CS_DESC_LONG").text

                associated_competencies = (
                    competencyExtractor.extract_competencies(
                        course_description
                    )
                )

                try:
                    db.create_course(
                        course_description, associated_competencies
                    )
                except CourseInsertionFailed as e:
                    return Response(
                        f"error: {e}", status=400, mimetype="application/json"
                    )

            db.close()
            return "Imported Courses from XML File successfully!"
    else:
        return Response(
            "Content-Type not supported! Expected type application/json or multipart/form-data",
            status=400,
            mimetype="application/json",
        )


@app.route("/courses", methods=["GET"])
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

    return jsonify([course.toJSON() for course in courses])


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

    return jsonify([competency.toJSON() for competency in competencies])
