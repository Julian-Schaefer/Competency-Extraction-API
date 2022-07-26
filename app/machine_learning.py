import os
from typing import List
import pandas as pd
import re
import ast
import spacy
from spacy.tokens import DocBin


def __create_spacy_file__(course_descriptions: List[str], competencies: List[List[str]], train_or_test: str) -> None:
    data = []
    for i, course_descr in enumerate(course_descriptions):
        comp = competencies[i]
        comp = pd.unique(comp).tolist()
        # check if course has competencies
        if len(comp) != 0:
            indices = []
            for c in comp:
                for m in re.finditer(
                    "(\.| )" + c + "(\.| )", " " + course_descr + " "
                ):
                    indices.append(
                        (m.start(), m.start() + len(c), "COMPETENCY")
                    )
            data.append((course_descr, indices))
        else:
            data.append((course_descr, []))

    # check for overlapping annotations and only keep the first one
    data2 = []
    for text, annotations in data:
        if len(annotations) == 0:
            data2.append((text, annotations))
        else:
            annotations_new = [annotations[0]]
            spans = []
            for start, end, _ in annotations:
                spans.append(pd.Interval(start, end, closed="both"))

            for i, span in enumerate(spans):
                if i == 0:
                    continue
                else:
                    overlap = False
                    for span_x in spans[0:i]:
                        if span.overlaps(span_x):
                            overlap = True
                    if not overlap:
                        annotations_new.append(annotations[i])
            data2.append((text, annotations_new))

    nlp = spacy.blank("de")
    db = DocBin()
    for i, (text, annotations) in enumerate(data2):
        doc = nlp(text)
        ents = []
        for start, end, label in annotations:
            span = doc.char_span(start, end, label=label)
            ents.append(span)
        doc.ents = ents
        db.add(doc)
    db.to_disk(os.environ.get("ML_DIR") + train_or_test + ".spacy")


def create_train_and_test_spacy_files(frac=0.8) -> None:
    """
    Creates spacy training and testing files for training a NER model.
    The data used to make the files comes from the courses_preprocessed.csv which contains the competencies that the
    Reference Implementation extracted from the course descriptions provided by
    the Weiterbildungsdatenbank Berlin Brandenburg.
    The files are saved in the in the sub directory "ML".
    :param frac: The fraction of training data.
    :type frac: int
    """
    # load course DataFrame and delete rows with no preprocessed course description
    courses_df = pd.read_csv(
        os.environ.get("COURSES_FILE"),
        sep="|",
        encoding="utf-8",
        index_col=0,
    )[["course_descr_long_preprocessed", "competencies"]]
    courses_df = courses_df[
        ~courses_df["course_descr_long_preprocessed"].isna()
    ]
    courses_df["competencies"] = courses_df["competencies"].map(ast.literal_eval)
    # split DataFrame into training and testing
    training_data_df = courses_df.sample(frac=frac, random_state=25)
    testing_data_df = courses_df.drop(training_data_df.index)
    # create spacy files for training and testing
    __create_spacy_file__(training_data_df["course_descr_long_preprocessed"].tolist(),
                              training_data_df["competencies"].tolist(),
                              "train")
    __create_spacy_file__(testing_data_df["course_descr_long_preprocessed"].tolist(),
                              testing_data_df["competencies"].tolist(),
                              "test")


create_train_and_test_spacy_files()
