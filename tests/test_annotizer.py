from app.annotizer import Annotizer


def test_annotize():
    annotizer = Annotizer()
    competencies = annotizer.annotize(
        "Musikpersonal verwalten ist ein anstrengender Skill. Es ist aber sehr hilfreich."
    )

    assert len(competencies) == 1
