from flask import Blueprint, Response, request, json, jsonify
from app.db import (
    CourseAlreadyExists,
    GraphDatabaseConnection,
    CourseInsertionFailed,
    RetrievingCourseFailed,
    RetrievingCompetencyFailed,
)
from app.store import Store, StoreAlreadyInitialized
from app.competency_extractor import (
    MLCompetencyExtractor,
    PaperCompetencyExtractor,
)
import xml.etree.ElementTree as ET
from app.models import Course

routes = Blueprint("routes", __name__)


@routes.route("/")
def hello():
    return "<h1>Welcome!</h1><p>Welcome to our API server, you can query courses and competencies here.</p>"


@routes.route("/competencies/initialize", methods=["POST"])
def initialize():
    store = Store()
    try:
        store.initialize()
        return "Database and Store have been initialized with Competencies successfully!"
    except StoreAlreadyInitialized:
        return "Database and Store have already been initialized.", 409


def _get_competency_extractor_from_string(name):
    if name == "paper":
        return PaperCompetencyExtractor()
    elif name == "ml":
        return MLCompetencyExtractor()

    return None


@routes.route("/courses", methods=["POST"])
def create_course():
    extractor = request.args.get("extractor")
    if not extractor:
        extractor = "paper"

    if request.headers.get("Content-Type") == "application/json":
        course_description = json.loads(request.data).get("courseDescription")

        if not course_description:
            return {"error": "Body 'course_description' is missing"}, 400

        competencyExtractor = _get_competency_extractor_from_string(
            name=extractor
        )

        associated_competencies = competencyExtractor.extract_competencies(
            [course_description]
        )[0]

        db = GraphDatabaseConnection()

        try:
            course = db.create_course(
                course_description, extractor, associated_competencies
            )
        except CourseAlreadyExists as e:
            return {"error": str(e)}, 409
        except CourseInsertionFailed as e:
            return {"error": str(e)}, 400

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
            return {
                "error": "An error occured while reading the file. Please make sure to upload a correctly formatted XML file named as 'courses'."
            }, 400

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
                        course_description,
                        extractor,
                        associated_competencies[i],
                    )
                except CourseAlreadyExists as e:
                    return {"error": str(e)}, 409
                except CourseInsertionFailed as e:
                    return {"error": str(e)}, 400

            db.close()
            return "Imported Courses from XML File successfully!"
    else:
        return {
            "error": "Content-Type not supported! Expected type application/json or multipart/form-data"
        }, 400


@routes.route("/courses", methods=["GET"])
def retrieve_course():
    competency_id = request.args.get("competencyId")
    text_search_query = request.args.get("search")

    db = GraphDatabaseConnection()

    # in case the request body contains a competency_id, filter courses
    try:
        if competency_id:
            courses = db.find_courses_by_competency(int(competency_id))
        elif text_search_query and len(text_search_query) > 0:
            courses = db.find_courses_by_text_query(text_search_query)
        else:
            courses = db.retrieve_all_courses()
    except RetrievingCourseFailed as e:
        return {"error": str(e)}, 400

    db.close()

    return jsonify([course.toJSON() for course in courses])


@routes.route("/competencies", methods=["GET"])
def retrieve_competency():
    course_id = request.args.get("courseId")
    text_search_query = request.args.get("search")

    db = GraphDatabaseConnection()

    try:
        if course_id:
            competencies = db.find_competencies_by_course(int(course_id))
        elif text_search_query and len(text_search_query) > 0:
            competencies = db.find_competencies_by_text_query(
                text_search_query
            )
        else:
            competencies = db.retrieve_all_competencies()
    except RetrievingCompetencyFailed as e:
        return {"error": str(e)}, 400

    db.close()

    return jsonify([competency.toJSON() for competency in competencies])


@routes.route("/courses/export", methods=["POST"])
def export_courses():

    file_path = "data/exported_courses.json"

    f = open(file_path, "w")

    db = GraphDatabaseConnection()

    try:
        courses = db.retrieve_all_courses()
    except RetrievingCompetencyFailed as e:
        return Response(f"error: {e}", status=400, mimetype="application/json")

    db.close()

    courses_with_competencies = []

    for course in courses:
        course_id = course.id
        try:
            competencies = db.find_competencies_by_course(course_id)
        except RetrievingCompetencyFailed as e:
            return Response(
                f"error: {e}", status=400, mimetype="application/json"
            )
        courses_with_competencies.append(
            Course(
                course.id, course.description, course.extractor, competencies
            )
        )

    json_string = json.dumps(
        [course.toJSON() for course in courses_with_competencies]
    )

    f.write(json_string)

    return f"Database export was written into '{file_path}'."
