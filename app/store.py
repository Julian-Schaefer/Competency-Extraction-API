import os
from app.db import GraphDatabaseConnection
import pandas
from app.lemmaCache import LemmatizerGerman
import requests


class Store:
    baseUrl = "https://ec.europa.eu/esco/api"

    def __init__(self, language="de"):
        self.language = language
        self.db = GraphDatabaseConnection()
        self.lemmatizer = LemmatizerGerman()

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
        query = {"text": term, "language": self.language}
        response = requests.get(self.baseUrl + "/terms", params=query)
        json = response.json()
        return json["total"] > 0

    def check_sequence(self, sequence):
        query = {"text": sequence, "language": self.language}
        response = requests.get(self.baseUrl + "/suggest2", params=query)
        json = response.json()
        return json["_embedded"]["results"]
