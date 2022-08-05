"""
store.py
====================================
Allows Initialization of the Database with Competencies and provides the termStore as well as the sequenceStore.
"""

from typing import Union
import os
from db import GraphDatabaseConnection
import pandas
from preprocessing_utils import PreprocessorGerman
from models import Competency, Label
from typing import List


class StoreAlreadyInitialized(Exception):
    """Raised when the Store has already been initialized."""

    pass


class Store:
    """
    The Store class provides the functionality to initialize the Graph Database with EU-ESCO competencies.
    Furthermore, it also acts as the termStore and as the sequenceStore which are used by
    the :class:`app.competency_extractor.PaperCompetencyExtractor` class.

    :param language: Language to use (defaults to German)
    :type language: str
    :ivar preprocessor: An instance of the :class:`app.preprocessing_utils.PreprocessorGerman` class to preprocess the labels of Competencies
    :type preprocessor: PreprocessorGerman
    """

    def __init__(self, language="de"):
        self.db = GraphDatabaseConnection()

        if language == "de":
            self.preprocessor = PreprocessorGerman()

    def initialize(self):
        """
        Initializes the Database with Competencies imported from a EU-ESCO compatible .csv File.
        The Location of the .csv file has to be specified using the environment variable "DATA_FILE"
        """
        existing_competencies = self.db.retrieve_all_competencies()
        if existing_competencies and len(existing_competencies) > 0:
            raise StoreAlreadyInitialized()

        competencies = []

        skills = self.preprocessor.get_skills_from_file_as_json()

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

    def check_term(self, term: str) -> bool:
        """
        Check if a term is contained in the term store.

        :param term: A single term
        :type term: str
        :return: True if the term is contained in the term store and False if not
        :rtype: bool
        """
        is_found = self.db.find_label_by_term(term)
        return is_found

    def check_sequence(
        self, sequence: Union[str, List[str]]
    ) -> List[Competency]:
        """
        Check if a sequence of words is contained in the sequence store and return all competencies with a label that matches
        the sequence.

        :param sequence: A sequence of words as a list of string tokens or as string
        :type sequence: Union[str, List[str]]

        :return: A list of all competencies contained in the sequence store, whose labels match the given sequence.
        :rtype: List[Competency]
        """
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

    :ivar preprocessor: An instance of the :class:`app.preprocessing_utils.PreprocessorGerman` class to preprocess the labels of Competencies
    :type preprocessor: PreprocessorGerman
    :ivar store_df: A DataFrame representation of a .csv file (located by the Environment Variable "LABELED_COMPETENCIES_FILE") which contains all preferred and alternative labels that are contained in the EU ESCO API.
    :type store_df: DataFrame
    """

    def __init__(self) -> None:
        """
        Constructor method
        """
        self.preprocessor = PreprocessorGerman()
        self.store_df = pandas.read_csv(
            os.environ.get("LABELED_COMPETENCIES_FILE"),
            index_col=0,
        )

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

        :param sequence: A sequence of words as a list of string tokens
        :type sequence: List[str]

        :return: A list of all competencies contained in the sequence store, whose labels match the given sequence.
        :rtype: List[str]
        """
        if len(sequence) == 0:
            return []
        sequence_string = " ".join(sequence)
        competencies = self.store_df[self.store_df["label"] == sequence_string]
        return competencies["label"].tolist()
