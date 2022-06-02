import os
from app.db import GraphDatabaseConnection
import pandas


class Store:
    def __init__(self, language="de"):
        self.db = GraphDatabaseConnection()

        if language == "de":
            self.lemmatizer = LemmatizerGerman()
        elif language == "en":
            self.lemmatizer = LemmatizerEnglish()

    def initialize(self):
        data_file = pandas.read_csv(os.environ.get("DATA_FILE"))
        data_file["altLabels"] = data_file["altLabels"].astype("string")

        for _, row in data_file.iterrows():
            lemmatized_label = self.lemmatizer.lemmatize_spacy(
                row["preferredLabel"]
            )
            labels = [
                {"text": " ".join(lemmatized_label), "type": "preferred"}
            ]

            if not pandas.isna(row["altLabels"]):
                alt_labels = row["altLabels"].split("\n")
                lemmatized_labels = [
                    self.lemmatizer.lemmatize_spacy(alt_label)
                    for alt_label in alt_labels
                ]
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
        competencies = self.db.find_competency_by_sequence(sequence)
        return competencies
