import os
from app.db import GraphDatabaseConnection
import pandas
from app.preprocessing_utils import PreprocessorGerman


class Store:
    def __init__(self, language="de"):
        self.db = GraphDatabaseConnection()

        if language == "de":
            self.lemmatizer = PreprocessorGerman()

    def initialize(self):
        data_file = pandas.read_csv(os.environ.get("DATA_FILE"))
        data_file["altLabels"] = data_file["altLabels"].astype("string")

        for _, row in data_file.iterrows():
            lemmatized_label = self.lemmatizer.preprocess_course_descriptions(
                [row["preferredLabel"]]
            )[0]
            labels = [
                {"text": " ".join(lemmatized_label), "type": "preferred"}
            ]

            if not pandas.isna(row["altLabels"]):
                alt_labels = row["altLabels"].split("\n")
                lemmatized_labels = (
                    self.lemmatizer.preprocess_course_descriptions(alt_labels)
                )

                labels += [
                    {"text": " ".join(lemmatized_label), "type": "alternative"}
                    for lemmatized_label in lemmatized_labels
                ]

            skill = {
                "conceptType": row["conceptType"],
                "conceptUri": row["conceptUri"],
                "skillType": row["skillType"],
                "description": row["description"],
                "labels": labels,
            }

            self.db.create_competency(skill)

    def check_term(self, term):
        is_found = self.db.find_label_by_term(term)
        return is_found

    def check_sequence(self, sequence):
        sequence_string = " ".join(sequence)
        competencies = self.db.find_competency_by_sequence(sequence_string)
        return competencies
