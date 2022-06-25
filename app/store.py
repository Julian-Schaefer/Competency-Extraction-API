import os
from app.db import GraphDatabaseConnection
import pandas
from app.preprocessing_utils import PreprocessorGerman
from app.models import Competency, Label


class Store:
    def __init__(self, language="de"):
        self.db = GraphDatabaseConnection()

        if language == "de":
            self.lemmatizer = PreprocessorGerman()

    def initialize(self):
        data_file = pandas.read_csv(os.environ.get("DATA_FILE"))
        data_file["altLabels"] = data_file["altLabels"].astype("string")

        competencies = []

        skills = self.lemmatizer.get_skills_from_file_as_json(
            os.environ.get("DATA_FILE")
        )

        for uri, skill in skills.items():
            labels = [
                Label(
                    text=" ".join(skill["preferredLabelPreprocessed"]),
                    type="preferred",
                )
            ]

            if skill.get("altLabelsPreprocessed"):
                labels += [
                    Label(
                        text=" ".join(preprocessed_label), type="alternative"
                    )
                    for preprocessed_label in skill["altLabelsPreprocessed"]
                ]

            competency = Competency(
                conceptType=skill["conceptType"],
                conceptUri=uri,
                competencyType=skill["skillType"],
                description=skill["description"],
                labels=labels,
            )

            competencies += [competency]

        self.db.create_competencies(competencies)

    def check_term(self, term):
        is_found = self.db.find_label_by_term(term)
        return is_found

    def check_sequence(self, sequence):
        if len(sequence) == 0:
            return []

        sequence_string = " ".join(sequence)
        competencies = self.db.find_competency_by_sequence(sequence_string)
        return competencies
