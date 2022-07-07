import pandas as pd
import re
import ast
import spacy
from spacy.tokens import DocBin


def create_spacy_file_from_df(df, train_or_test: str) -> None:
    course_descrs = df["course_descr_long_preprocessed"].tolist()
    comps = df["competencies"].tolist()

    data = []
    for i, course_descr in enumerate(course_descrs):
        comp = ast.literal_eval(comps[i])
        comp = pd.unique(comp).tolist()
        # check if course has competencies
        if len(comp) != 0:
            indices = []
            for c in comp:
                for m in re.finditer("(\.| )" + c + "(\.| )", " " + course_descr + " "):
                    indices.append((m.start(), m.start() + len(c), "COMPETENCY"))
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
    end_of_loop = len(data2)
    for i, (text, annotations) in enumerate(data2):
        doc = nlp(text)
        ents = []
        for start, end, label in annotations:
            span = doc.char_span(start, end, label=label)
            ents.append(span)
        doc.ents = ents
        db.add(doc)
    db.to_disk("./" + train_or_test + ".spacy")


def main():
    # load course DataFrame and delete rows with no preprocessed course description
    courses_df = pd.read_csv(r"C:\Users\amirm\OneDrive\Desktop\Python "
                             r"Projects\AWT-Project\data\courses_preprocessed.csv", sep="|", encoding="utf-8",
                             index_col=0)[['course_descr_long_preprocessed', "competencies"]]
    courses_df = courses_df[~courses_df["course_descr_long_preprocessed"].isna()]
    # split DataFrame into training and testing
    training_data_df = courses_df.sample(frac=0.8, random_state=25)
    testing_data_df = courses_df.drop(training_data_df.index)

    # create spacy files for training and testing
    create_spacy_file_from_df(training_data_df, "train")
    create_spacy_file_from_df(testing_data_df, "test")
