from typing import List, Optional, Dict
from typing import List, Dict
from app.models import Competency
from app.store import Store


class CompetencyExtractorInterface:
    """Interface for Competency Extractors"""

    def extract_competencies(
        self, course_description: str
    ) -> List[Optional[Dict]]:
        """Extract competencies from course_description."""
        pass


class DummyExtractor(CompetencyExtractorInterface):
    """Dummy extractor for testing."""

    def extract_competencies(
        self, course_description: str
    ) -> List[Optional[Dict]]:
        """Extract competencies

        Extract competencies from course_description returning every word.

        Parameters:
            course_description: course body as string

        Returns:
            List of competencies as dict
        """
        return [
            {"name": c, "body": f"some description of {c}"}
            for c in course_description.split()
        ]


class PaperCompetencyExtractor(CompetencyExtractorInterface):
    def __init__(self):
        self.store = Store()
        self.lemmatizer = self.store.lemmatizer

    def extract_competencies(
        self, course_description: str
    ) -> List[Competency]:
        tt = self.lemmatizer.preprocess_course_descriptions(
            [course_description]
        )[0]

        at = ""
        all_competencies = []
        p = 0

        for token in tt:
            p = p + 1
            if not self.store.check_term(token):
                at = at + " " + token
            else:
                (phrase, _) = self.lookahead(tt[(p):], [token], 1)
                if len(phrase) > 0:
                    competencies = self.store.check_sequence(phrase)
                    if len(competencies) > 0:
                        all_competencies += competencies
                        at = at + " " + " ".join(phrase)
                        continue

                at = at + " " + token

        return all_competencies

    def lookahead(self, tt, fp, n):
        if len(tt) == 0:
            return (fp, n)

        termfound = self.store.check_term(tt[0])
        phraseFound = len(self.store.check_sequence(fp)) > 0

        if termfound or phraseFound:
            new_fp = fp[:]
            new_fp.append(tt[0])
            (ph, l) = self.lookahead(tt[1:], new_fp, n + 1)
            if len(self.store.check_sequence(ph)) > 0:
                return (ph, l)
            elif phraseFound:
                return (fp, n)

        return ([], n)
