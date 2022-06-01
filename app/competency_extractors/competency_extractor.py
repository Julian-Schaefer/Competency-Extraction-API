from typing import List, Optional, Dict
from app import text_processing_utils
from app import store
from itertools import groupby
from typing import List, Tuple, Dict


class CompetencyExtractorInterface:
    """Interface for Competency Extractors"""

    def extract_competencies(self, course_body: str) -> List[Optional[Dict]]:
        """Extract competencies from course_body."""
        pass


class DummyExtractor(CompetencyExtractorInterface):
    """Dummy extractor for testing."""

    def extract_competencies(self, course_body: str) -> List[Optional[Dict]]:
        """Extract competencies

        Extract competencies from course_body returning every word.

        Parameters:
            course_body: course body as string

        Returns:
            List of competencies as dict
        """
        return [
            {"name": c, "body": f"some description of {c}"}
            for c in course_body.split()
        ]


class Dummy2Extractor(CompetencyExtractorInterface):

    def __init__(self):
        self.lemmatizer_de = text_processing_utils.TextProcessorGerman()
        self.store = store.Store()

    def extract_sequences_from_sentence(self, sentence):
        is_in_term_store = []
        for token in sentence:
            if self.store.check_term(token):
                is_in_term_store.append(token)
            else:
                is_in_term_store.append(None)
        sequences = (list(g) for _, g in groupby(is_in_term_store, key=None.__ne__))
        print([x for x in sequences if x != [None]])
        return [x for x in sequences if x != [None]]

    def extract_competencies_from_sentence(self, sentence):
        return self.extract_sequences_from_sentence(sentence)

    def extract_competencies(self, course_body: str) -> List[Optional[Dict]]:
        # lemmatize course
        course_body = self.lemmatizer_de.lemmatize_hannover(course_body)
        # Loop over sentences
        for sentence in course_body:
            self.extract_competencies_from_sentence(sentence)


class Dummy3Extractor(CompetencyExtractorInterface):

    def __init__(self):
        self.lemmatizer_de = text_processing_utils.TextProcessorGerman()
        self.store = store.Store()

    def extract_competencies_from_sentence(self, sentence):
        p = 0
        at = ""
        a = []
        for token in sentence:
            p += 1





    def extract_competencies(self, course_body: str) -> List[Optional[Dict]]:
        # lemmatize course
        course_body = self.lemmatizer_de.lemmatize_hannover(course_body)
        # Loop over sentences
        for sentence in course_body:
            self.extract_competencies_from_sentence(sentence)




