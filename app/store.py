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

        competencies = []

        for _, row in data_file.iterrows():
            preprocessed_label = self.lemmatizer.preprocess_label(
                row["preferredLabel"]
            )
            labels = [
                {"text": " ".join(preprocessed_label), "type": "preferred"}
            ]

            if not pandas.isna(row["altLabels"]):
                alt_labels = row["altLabels"].split("\n")
                preprocessed_labels = [
                    self.lemmatizer.preprocess_label(alt_label)
                    for alt_label in alt_labels
                ]

                labels += [
                    {
                        "text": " ".join(preprocessed_label),
                        "type": "alternative",
                    }
                    for preprocessed_label in preprocessed_labels
                ]

            competency = {
                "conceptType": row["conceptType"],
                "conceptUri": row["conceptUri"],
                "competencyType": row["skillType"],
                "description": row["description"],
                "labels": labels,
            }

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
