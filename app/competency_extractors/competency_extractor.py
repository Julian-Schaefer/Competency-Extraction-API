from typing import List, Optional, Dict


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
