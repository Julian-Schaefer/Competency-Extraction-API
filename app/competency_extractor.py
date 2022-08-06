"""
competency_extractor.py
====================================
Defines the generic interface of a Competency Extractor and also contains different implementations of Competency Extractors.
"""

from typing import List, Tuple
from app.models import Competency
from app.store import Store, StoreLocal
import pandas as pd
import spacy
import os


class CompetencyExtractorInterface:
    """Defines the basic Interface for Competency Extractors"""

    def extract_competencies(
        self, course_descriptions: List[str]
    ) -> List[List[Competency]]:
        """Extract competencies from Course Descriptions.

        :param course_descriptions: A List of Course Descriptions
        :type course_descriptions: List[str]

        :return: For each course description a list of competencies that have been extracted.
        :rtype: List[List[Competency]]
        """
        pass


class DummyCompetencyExtractor(CompetencyExtractorInterface):
    """A First Dummy Competency Extractor used only for testing and initial setup."""

    def extract_competencies(
        self, course_descriptions: List[str]
    ) -> List[List[Competency]]:
        """Extract competencies from Course Descriptions.

        :param course_descriptions: A List of Course Descriptions
        :type course_descriptions: List[str]

        :return: For each course description a list of competencies that have been extracted.
        :rtype: List[List[Competency]]
        """
        return [
            Competency(
                preferredLabel=course_description,
                description=f"some description of {course_description.split()}",
            )
            for course_description in course_descriptions
        ]


class PaperCompetencyExtractor(CompetencyExtractorInterface):
    """
    This Competency Extractor implements the approach/algorithm presented by the paper
    "Ontology-based Entity Recognition and Annotation" (available at http://ceur-ws.org/Vol-2535/paper_4.pdf).
    It is used as the reference implementation that can be used to compare results to
    other implementations of Competency Extractors.

    :ivar store: An Instance of a Store to check labels and sequences
    :type store: Store
    :ivar preprocessor: An instance of the :class:`app.preprocessing_utils.PreprocessorGerman` class to preprocess the labels of Competencies
    :type preprocessor: PreprocessorGerman
    """

    def __init__(self):
        self.store = Store()
        self.preprocessor = self.store.preprocessor

    def extract_competencies(
        self, course_descriptions: List[str]
    ) -> List[List[Competency]]:
        """Extract competencies from Course Descriptions.

        :param course_descriptions: A List of Course Descriptions
        :type course_descriptions: List[str]

        :return: For each course description a list of competencies that have been extracted.
        :rtype: List[List[Competency]]
        """
        tokenized_texts = self.preprocessor.preprocess_texts(
            course_descriptions
        )

        tokenized_texts_series = pd.Series(tokenized_texts, name="form")
        competencies = tokenized_texts_series.map(
            lambda tokenized_text: self._get_competencies_from_tokenized_text(
                tokenized_text
            )
        )

        competencies = competencies.tolist()
        return competencies

    def _get_competencies_from_tokenized_text(
        self, tokenized_text: List[str]
    ) -> List[Competency]:
        """
        Implementation of the "annotate" function defined by the Paper Algorithm.
        """
        at = ""
        all_competencies = []
        p = 0

        for token in tokenized_text:
            p = p + 1
            if not self.store.check_term(token):
                at = at + " " + token
            else:
                (phrase, _) = self._lookahead(tokenized_text[p:], [token], 1)
                if len(phrase) > 0:
                    competencies = self.store.check_sequence(phrase)
                    if len(competencies) > 0:
                        all_competencies += competencies
                        at = at + " " + " ".join(phrase)
                        continue

                at = at + " " + token

        return all_competencies

    def _lookahead(
        self, tokenized_text: List[str], fp: List[str], n: int
    ) -> Tuple[List[str], int]:
        """
        Implementation of the "lookahead" function defined by the Paper Algorithm.
        """
        if len(tokenized_text) == 0:
            return (fp, n)

        termfound = self.store.check_term(tokenized_text[0])
        phraseFound = len(self.store.check_sequence(fp)) > 0

        if termfound or phraseFound:
            new_fp = fp[:]
            new_fp.append(tokenized_text[0])
            (ph, l) = self._lookahead(tokenized_text[1:], new_fp, n + 1)
            if len(self.store.check_sequence(ph)) > 0:
                return (ph, l)
            elif phraseFound:
                return (fp, n)

        return ([], n)


class PaperCompetencyExtractorLocal(PaperCompetencyExtractor):
    """
    This class contains the same functionality as the PaperCompetencyExtractor class. The only difference is that this
    class can be used to extract competencies from course descriptions locally, without having to start the server.
    Extracting competencies through this class however does not upload the courses and extracted competencies to the
    Database. The only purpose of this class is to extract competencies in big batches in order to evaluate the results and
    compare them to the results of other extractors.

    :ivar store: An Instance of a local Store to check labels and sequences
    :type store: StoreLocal
    :ivar preprocessor: An instance of the :class:`app.preprocessing_utils.PreprocessorGerman` class to preprocess the labels of Competencies
    :type preprocessor: PreprocessorGerman
    """

    def __init__(self):
        self.store = StoreLocal()
        self.preprocessor = self.store.preprocessor


class MLCompetencyExtractor(CompetencyExtractorInterface):
    """
    This Competency Extractor uses a Machine Learning Model that has been trained on a Dataset which was generated using
    the reference Competency Extractor, namely :class:`app.competency_extractor.PaperCompetencyExtractor`.

    :ivar store: An Instance of a Store which provides the Preprocessor
    :type store: Store
    :ivar preprocessor: An instance of the :class:`app.preprocessing_utils.PreprocessorGerman` class to preprocess the labels of Competencies
    :type preprocessor: PreprocessorGerman
    :ivar nlp: An instance of a spaCy model, which is loaded from the location of the "MODEL_FILES" environment variable
    :type nlp: spacy.Language
    """

    def __init__(self):
        self.store = Store()
        self.preprocessor = self.store.preprocessor
        self.nlp = spacy.load(os.environ.get("MODEL_FILES"))

    def extract_competencies(
        self, course_descriptions: List[str]
    ) -> List[List[Competency]]:
        """Extract competencies from Course Descriptions.

        :param course_descriptions: A List of Course Descriptions
        :type course_descriptions: List[str]

        :return: For each course description a list of competencies that have been extracted.
        :rtype: List[List[Competency]]
        """
        tokenized_texts = self.preprocessor.preprocess_texts(
            course_descriptions
        )
        texts = self.preprocessor.join_tokenized_texts(tokenized_texts)
        all_competencies = []

        for text in texts:
            doc = self.nlp(text)
            entities = doc.ents

            course_competencies = []
            for entity in entities:
                competencies = self.store.check_sequence(
                    entity.text.split(" ")
                )
                course_competencies += competencies

            all_competencies += [course_competencies]

        return all_competencies


class MLCompetencyExtractorLocal(MLCompetencyExtractor):
    def __init__(self):
        self.nlp = spacy.load(os.environ.get("MODEL_FILES"))
        self.store = StoreLocal()
        self.preprocessor = self.store.preprocessor
