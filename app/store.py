import os
from app.db import GraphDatabaseConnection
import pandas
from app.preprocessing_utils import PreprocessorGerman
from app.models import Competency, Label
from pandas import DataFrame
from typing import List


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
                skillType=skill["skillType"],
                reuseLevel=skill["reuseLevel"],
                preferredLabel=skill["preferredLabel"],
                altLabels=skill["altLabels"],
                hiddenLabels=skill["hiddenLabels"],
                status=skill["status"],
                modifiedDate=skill["modifiedDate"],
                scopeNote=skill["scopeNote"],
                definition=skill["definition"],
                inScheme=skill["inScheme"],
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

        if isinstance(sequence, str):
            sequence_string = sequence
        else:
            sequence_string = " ".join(sequence)

        competencies = self.db.find_competency_by_sequence(sequence_string)
        return competencies


class StoreLocal:
    """
    The StoreLocal class provides the same functionality as the Store class. The only difference is that the StoreLocal
    class can be used locally without having to start the server and without having to connect to the Database.
    :param prc: A instance of the PreprocessorGerman class
    :type prc: PreprocessorGerman
    :param store_df: A DataFrame representation of the all_skill_labels.csv which contains all preferred and alternative
    labels that are contained in the EU ESCO API.
    :type store_df: DataFrame
    """
    def __init__(self) -> None:
        """
        Constructor method
        """
        self.prc = PreprocessorGerman()
        self.store_df = pandas.read_csv(
            r"C:\Users\amirm\OneDrive\Desktop\Python Projects\AWT-Project\app\all_skill_labels.csv",
            index_col=0,
        )  ## change later

    def check_term(self, term: str) -> bool:
        """
        Check if a term is contained in the term store.
        :param term: A single term
        :type term: str
        :return: True if the term is contained in the term store and False if not
        :rtype: bool
        """
        return (
            self.store_df[self.store_df["label"].str.contains(term)].shape[0]
            > 0
        )

    def check_sequence(self, sequence: List[str]) -> List[str]:
        """
        Check if a sequence is contained in the sequence store and return all competencies with a label that matches
        the sequence.
        :param sequence: A sequence of words as a list of tokens
        :type sequence: List[str]
        :return: A list of all competencies contained in the sequence store, whose labels match the given sequence.
        :rtype: List[str]
        """
        if len(sequence) == 0:
            return []
        sequence_string = " ".join(sequence)
        competencies = self.store_df[self.store_df["label"] == sequence_string]
        return competencies["label"].tolist()
