from flask import Flask, Response, request, json, jsonify
from app.db import (
    GraphDatabaseConnection,
    CourseInsertionFailed,
    RetrievingCourseFailed,
    RetrievingCompetencyFailed,
)
from app.store import Store
from app.competency_extractors.competency_extractor import (
    MLCompetencyExtractor,
    PaperCompetencyExtractor,
)
import xml.etree.ElementTree as ET

app = Flask(__name__, static_folder="../docs", static_url_path="/docs")


@app.route("/")
def hello():
    return "<h1>Welcome!</h1><p>Welcome to our API server, you can query courses and competencies here.</p>"


@app.route("/initialize", methods=["POST"])
def initialize():
    store = Store()
    store.initialize()
    return "Database and Store have been initialized successfully!"


def _get_competency_extractor_from_string(name):
    if not name or name == "paper":
        return PaperCompetencyExtractor()
    elif name == "ml":
        return MLCompetencyExtractor()

    return None


@app.route("/course", methods=["POST"])
def create_course():
    extractor = request.args.get("extractor")

    if request.headers.get("Content-Type") == "application/json":
        course_description = json.loads(request.data).get("courseDescription")

        if not course_description:
            return Response(
                "Body 'course_description' is missing",
                status=400,
                mimetype="application/json",
            )

        competencyExtractor = _get_competency_extractor_from_string(
            name=extractor
        )

        associated_competencies = competencyExtractor.extract_competencies(
            [course_description]
        )[0]

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
            course_descriptions = []
            courses_file = request.files["courses"]

            courses_xml = ET.parse(
                courses_file.stream, parser=ET.XMLParser(encoding="utf-8")
            )
            courses = courses_xml.findall(".//COURSE")
            for course in courses:
                course_description = course.find("CS_DESC_LONG").text
                course_descriptions += [course_description]

        except:
            return Response(
                "An error occured while reading the file. Please make sure to upload a correctly formatted XML file named as 'courses'.",
                status=400,
                mimetype="application/json",
            )

        if len(course_descriptions) > 0:
            competencyExtractor = _get_competency_extractor_from_string(
                name=extractor
            )
            db = GraphDatabaseConnection()

            associated_competencies = competencyExtractor.extract_competencies(
                course_descriptions
            )

            for i, course_description in enumerate(course_descriptions):
                try:
                    db.create_course(
                        course_description, associated_competencies[i]
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
