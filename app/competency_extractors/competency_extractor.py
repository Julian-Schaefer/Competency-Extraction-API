from typing import List, Optional, Dict
from typing import List, Dict
from app.models import Competency
from app.store import Store, StoreLocal
import pandas as pd
import spacy
import os


class CompetencyExtractorInterface:
    """Interface for Competency Extractors"""

    def extract_competencies(
        self, course_descriptions: List[str]
    ) -> List[List[Competency]]:
        """Extract competencies from course_descriptions."""
        pass


class DummyExtractor(CompetencyExtractorInterface):
    """Dummy extractor for testing."""

    def extract_competencies(
        self, course_descriptions: List[str]
    ) -> List[List[Competency]]:
        """Extract competencies

        Extract competencies from course_description returning every word.

        Parameters:
            course_description: course body as string

        Returns:
            List of competencies as dict
        """
        return [
            {
                "name": course_description,
                "body": f"some description of {course_description.split()}",
            }
            for course_description in course_descriptions
        ]


class PaperCompetencyExtractor(CompetencyExtractorInterface):
    def __init__(self):
        self.store = Store()
        self.lemmatizer = self.store.lemmatizer

    def extract_competencies(
        self, course_descriptions: List[str]
    ) -> List[List[Competency]]:
        tokenized_texts = self.lemmatizer.preprocess_course_descriptions(
            course_descriptions
        )

        tokenized_texts_series = pd.Series(tokenized_texts, name="form")
        competencies = tokenized_texts_series.map(
            lambda tokenized_text: self.get_competencies_from_tokenized_text(
                tokenized_text
            )
        )

        competencies = competencies.tolist()
        return competencies

    def get_competencies_from_tokenized_text(self, tokenized_text):
        at = ""
        all_competencies = []
        p = 0

        for token in tokenized_text:
            p = p + 1
            if not self.store.check_term(token):
                at = at + " " + token
            else:
                (phrase, _) = self.lookahead(tokenized_text[(p):], [token], 1)
                if len(phrase) > 0:
                    competencies = self.store.check_sequence(phrase)
                    if len(competencies) > 0:
                        all_competencies += competencies
                        at = at + " " + " ".join(phrase)
                        continue

                at = at + " " + token

        return all_competencies

    def lookahead(self, tokenized_text, fp, n):
        if len(tokenized_text) == 0:
            return (fp, n)

        termfound = self.store.check_term(tokenized_text[0])
        phraseFound = len(self.store.check_sequence(fp)) > 0

        if termfound or phraseFound:
            new_fp = fp[:]
            new_fp.append(tokenized_text[0])
            (ph, l) = self.lookahead(tokenized_text[1:], new_fp, n + 1)
            if len(self.store.check_sequence(ph)) > 0:
                return (ph, l)
            elif phraseFound:
                return (fp, n)

        return ([], n)


class CompetencyExtractorPaperLocal(CompetencyExtractorInterface):
    def __init__(self):
        self.store = StoreLocal()

    def extract_competencies(
        self, course_descriptions: List[str]
    ) -> List[List[Competency]]:
        tokenized_texts = self.store.prc.preprocess_course_descriptions(
            course_descriptions
        )

        competencies = []
        for i, text in enumerate(tokenized_texts):
            leng = len(tokenized_texts)
            print(i + 1, " / ", leng)
            competencies.append(
                self.get_competencies_from_tokenized_text(text)
            )
        return competencies

    def get_competencies_from_tokenized_text(self, tokenized_text):
        at = ""
        all_competencies = []
        p = 0

        for token in tokenized_text:
            p = p + 1
            if not self.store.check_term(token):
                at = at + " " + token
            else:
                (phrase, _) = self.lookahead(tokenized_text[(p):], [token], 1)
                if len(phrase) > 0:
                    competencies = self.store.check_sequence(phrase)
                    if len(competencies) > 0:
                        all_competencies += competencies
                        at = at + " " + " ".join(phrase)
                        continue

                at = at + " " + token

        return all_competencies

    def lookahead(self, tokenized_text, fp, n):
        if len(tokenized_text) == 0:
            return (fp, n)

        termfound = self.store.check_term(tokenized_text[0])
        phraseFound = len(self.store.check_sequence(fp)) > 0

        if termfound or phraseFound:
            new_fp = fp[:]
            new_fp.append(tokenized_text[0])
            (ph, l) = self.lookahead(tokenized_text[1:], new_fp, n + 1)
            if len(self.store.check_sequence(ph)) > 0:
                return (ph, l)
            elif phraseFound:
                return (fp, n)

        return ([], n)


class MLCompetencyExtractor(CompetencyExtractorInterface):
    def __init__(self):
        self.store = Store()
        self.lemmatizer = self.store.lemmatizer
        self.nlp = spacy.load(os.environ.get("MODEL_FILES"))

    def extract_competencies(
        self, course_descriptions: List[str]
    ) -> List[List[Competency]]:
        tokenized_texts = self.lemmatizer.preprocess_course_descriptions(
            course_descriptions
        )

        all_competencies = []

        for tokenized_text in tokenized_texts:
            doc = self.nlp(" ".join(tokenized_text))
            entities = doc.ents

            course_competencies = []
            for entity in entities:
                competencies = self.store.check_sequence(entity.text)
                course_competencies += competencies

            all_competencies += [course_competencies]

        return all_competencies
