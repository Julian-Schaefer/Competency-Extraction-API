from app.annotizer import Annotizer


def test_annotize():
    annotizer = Annotizer()
    competencies = annotizer.annotize(
        "Musikpersonal verwalten ist ein anstrengender Skill. Es ist aber sehr hilfreich."
    )

    assert len(competencies) == 1


def test_annotize2():
    course_description = """Kurzbeschreibung
        Das Arbeitsrecht unterliegt einem ständigen Wandel durch Änderungen der Gesetzgebung und der folgenden Rechtsprechung. Im Seminar erhalten Sie notwendige
        Kenntnisse dieser Vorschriften bezogen auf soziale Einrichtungen, um rechtssicher zu handeln und unnötige gerichtliche Auseinandersetzungen zu vermeiden.

        - Beschäftigtendatenschutz nach EUDSGVO und BDSG
        - Urlaubsrecht, Urlaubsplanung, Verfall von Ansprüchen, Abgeltung von Urlaub
        - Qualifizierungsvereinbarungen mit Bindungsklausel
        - Befristung von Arbeitsverträgen mit und ohne Sachgrund
        - Inhaltliche Gestaltungsmöglichkeiten bei Arbeitsverträgen
        - Arbeitszeitrecht, Bereitschaftsdienste, Über- und Mehrstunden
        - Arbeitsrechtliche Sanktionen, Ermahnung, Abmahnung, Kündigung
        - Bedeutung des Eingliederungsmanagements bei personenbedingten Kündigungen wegen Krankheit
        - Übersicht aktueller Rechtsprechung der Arbeitsgerichte

        Aus Gründen der Aktualität können kurzfristig weitere Themen aufgenommen werden."""

    annotizer = Annotizer()
    competencies = annotizer.annotize(course_description)

    assert len(competencies) == 3
