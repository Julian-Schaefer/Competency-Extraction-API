import string
import pandas as pd
import nltk
import os
from typing import List
import numpy as np
from itertools import groupby, zip_longest
import json

__data_path__ = os.path.dirname(__file__) + "/lemma_cache_data"


def add_nltk_data_path():
    """
    Adds the directory ".\app\nltk_data" to the list of paths that the nltk library searches in for valid nltk models.
    """
    if not __data_path__ + "/nltk_data" in nltk.data.path:
        nltk.data.path.append(__data_path__ + "/nltk_data")


def split_list_by_dot(list_with_dot: List[str]) -> List[List[str]]:
    """
    Split a list into multiple lists based on elements that equal ".".
    :param list_with_dot: A List of string that contains dots
    :type list_with_dot: List[str]
    :return: A List of sublists
    :rtype: List[List[str]]
    """
    i = (list(g) for _, g in groupby(list_with_dot, key=".".__ne__))
    return [
        a + b if b != ["."] else a for a, b in zip_longest(i, i, fillvalue=[])
    ]


class PreprocessorGerman:
    """
    This class provides an interface for pre-processing course descriptions before parsing them into
    the entity recognition algorithm.
    """

    def __init__(self):
        add_nltk_data_path()
        self.morphys = pd.read_csv(
            __data_path__ + "/morphys.csv", encoding="utf-8", index_col=0
        )[["form", "lemma"]]
        self.language = "german"
        with open(
            __data_path__ + "/stopwords-de.txt", "r", encoding="utf-8"
        ) as f:
            self.stopwords = list(map(str.strip, list(f)))

    @staticmethod
    def convert_to_series(course_descriptions: List[str]) -> pd.Series:
        """
        Convert a list of course descriptions into a Pandas Series. Also remove any newline characters.
        :param course_descriptions: A List of course descriptions
        :type course_descriptions: List[str]
        :return: The list of course descriptions as a Pandas Series with newline characters removed
        :rtype: pd.Series[str]
        """
        return pd.Series(course_descriptions, name="form").map(
            lambda x: x.replace("\n", "")
        )

    def tokenize(self, course_descriptions: pd.Series) -> pd.Series:
        """
        Tokenize a Series of course descriptions.
        :param course_descriptions: A Series of course descriptions
        :type course_descriptions: pd.Series[str]
        :return: A Series of tokenized course descriptions, where each description is a Series itself
        :rtype: pd.Series[pd.Series[str]]
        """
        return course_descriptions.map(
            lambda x: pd.Series(
                nltk.word_tokenize(x, language=self.language), name="form"
            )
        )

    @staticmethod
    def remove_punctuation(course_descriptions: pd.Series) -> pd.Series:
        """
        Remove punctuation from a series of tokenized course descriptions. If a token only consists of punctuation
        characters it is removed entirely, unless the token is just one dot. In that case the token is kept.
        Hyphens that do not appear at the start or end of a token are not removed.
        :param course_descriptions: A Series of tokenized course descriptions
        :type course_descriptions: pd.Series[pd.Series[str]]
        :return: A Series of tokenized course descriptions with punctuation removed
        :rtype: pd.Series[pd.Series[str]]
        """
        punct = string.punctuation.replace("-", "")
        course_descriptions = course_descriptions.map(
            lambda x: x.where(
                x == ".",
                other=x.map(
                    lambda y: y.translate(str.maketrans("", "", punct)).strip(
                        "-"
                    )
                ),
            )
        )
        return course_descriptions.map(lambda x: x.drop(x[x == ""].index))

    @staticmethod
    def remove_numeric_tokens(course_descriptions: pd.Series) -> pd.Series:
        """
        Remove numeric tokens from a Series of tokenized course descriptions.
        :param course_descriptions: A Series of tokenized course descriptions
        :type course_descriptions: pd.Series[pd.Series[str]]
        :return: A Series of tokenized course descriptions with numeric tokens removed
        :rtype: pd.Series[pd.Series[str]]
        """
        return course_descriptions.map(lambda x: x[~x.str.isnumeric()])

    def remove_stopwords(self, course_descriptions: pd.Series) -> pd.Series:
        """
        Remove stopwords from a Series of tokenized course descriptions.
        :param course_descriptions: A Series of tokenized course descriptions
        :type course_descriptions: pd.Series[pd.Series[str]]
        :return: A Series of tokenized course descriptions with stopwords removed
        :rtype: pd.Series[pd.Series[str]]
        """
        return course_descriptions.map(
            lambda x: x[~x.str.lower().isin(self.stopwords)]
        )

    def lemmatize_morphys_fast(
        self, course_descriptions: pd.Series
    ) -> pd.Series:
        """
        Lemmatize a Series of tokenized course descriptions using the Morphys lookup table.
        Compound words that are written using hyphen notation, that do not appear in the lookup table are first split
        into their compounds, then the lemma for each compound is searched in the table, and finally the lemmas of
        each compound are joined back together separated by hyphens.
        If a token does not appear in the lookup table, the token itself is used as the lemma.
        :param course_descriptions: A Series of tokenized course descriptions
        :type course_descriptions: pd.Series[pd.Series[str]]
        :return: A Series of tokenized course descriptions where each token is lemmatized
        :rtype: pd.Series[pd.Series[str]]
        """
        ## get slices to split concatenated series back into original series
        indices_end = np.array(course_descriptions.map(len)).cumsum()
        indices_start = np.insert(indices_end[:-1], obj=0, values=0)
        slices = zip(indices_start, indices_end)

        ## concatenate all course descriptions into one series
        df = pd.concat(course_descriptions.tolist(), axis=0, ignore_index=True)

        ## expand morphys by lemmas of compounds terms seperated by hyphens
        df_hyphens = df[df.str.contains("-")]

        df_lemma_hyphens = df_hyphens.map(
            lambda x: "-".join(
                [
                    self.morphys[self.morphys["form"] == y]["lemma"].tolist()[
                        0
                    ]
                    if y in self.morphys["form"].tolist()
                    else y
                    for y in x.split("-")
                ]
            )
        ).rename("lemma")
        morphys_exp = pd.concat(
            [self.morphys, pd.concat([df_hyphens, df_lemma_hyphens], axis=1)]
        ).drop_duplicates(subset=["form"])

        ## lemmatize with expanded morphys dict
        df = pd.merge(left=df, right=morphys_exp, how="left")

        df = df["lemma"].fillna(df["form"])

        ## split back into original series
        return pd.Series([df.iloc[start:end] for start, end in slices])

    @staticmethod
    def lowercase(course_descriptions: pd.Series) -> pd.Series:
        """
        Lowercase a Series of tokenized course descriptions.
        :param course_descriptions: A Series of tokenized course descriptions
        :type course_descriptions: pd.Series[pd.Series[str]]
        :return: A Series of tokenized course descriptions with each token lowercased
        :rtype: pd.Series[pd.Series[str]]
        """
        return course_descriptions.map(lambda x: x.map(str.lower))

    def preprocess_course_descriptions(
        self, course_descriptions: List[str]
    ) -> List[List[str]]:
        """
        Preprocesses a list of course descriptions using the following pipeline:
        - tokenize
        - remove punctuation
        - remove numeric tokens
        - remove stopwords
        - lemmatize using the morphys lemmatizer
        - lowercase each token
        :param course_descriptions: A list of course descriptions
        :type course_descriptions: List[str]
        :return: The preprocessed course descriptions
        :rtype: List[List[str]]
        """
        # convert to series
        processed_course_descriptions = self.convert_to_series(
            course_descriptions
        )

        # tokenize
        processed_course_descriptions = self.tokenize(
            processed_course_descriptions
        )

        # remove punctuation
        processed_course_descriptions = self.remove_punctuation(
            processed_course_descriptions
        )

        # remove numeric tokens
        processed_course_descriptions = self.remove_numeric_tokens(
            processed_course_descriptions
        )

        # remove stopwords
        processed_course_descriptions = self.remove_stopwords(
            processed_course_descriptions
        )

        # lemmatize
        processed_course_descriptions = self.lemmatize_morphys_fast(
            processed_course_descriptions
        )

        # lowercase
        processed_course_descriptions = self.lowercase(
            processed_course_descriptions
        )

        return processed_course_descriptions.map(pd.Series.tolist).tolist()

    def get_skills_from_file_as_json(self, file) -> str:
        """
        Reads the "skills_de.csv" into a json string and preprocesses the labels of each skill.
        The resulting json string contains a dictionary. The keys are the concept-URIs. Each key has 5 fields:
        - conceptType: str
        - KnowledgeSkillCompetence: str
        - preferredLabel: str
        - altLabels: str
        - preferredLabelPreprocessed: List[str]
        - altLabelsPreprocessed: List[List[str]]

        The last two fields do not appear as columns in the "skills_de.csv" file. They are created within this method
        using the preprocessing pipeline.

        :return: json representation of the "skills_de.csv" file with added fields for the preprocessed labels
        :rtype: str
        """
        # import skills csv as DataFrame
        df = pd.read_csv(file, encoding="utf-8")[
            [
                "skillType",
                "conceptUri",
                "conceptType",
                "preferredLabel",
                "altLabels",
                "description",
            ]
        ]

        # Replace new line characters in the altLabels columns with dots
        df["altLabels"] = df["altLabels"].map(
            lambda x: x.replace("\n", ". ") if type(x) == str else x
        )

        # preprocess altLabels
        df_with_alt_label = df[~df["altLabels"].isna()][
            ["conceptUri", "altLabels"]
        ].reset_index(drop=True)
        df_with_alt_label["altLabels"] = df_with_alt_label["altLabels"]
        df_with_alt_label["altLabelsPreprocessed"] = pd.Series(
            self.preprocess_course_descriptions(
                df_with_alt_label["altLabels"].tolist()
            )
        )

        # preprocess preferredLabel
        df["preferredLabelPreprocessed"] = pd.Series(
            self.preprocess_course_descriptions(df["preferredLabel"])
        )

        # merge into one DataFrame and set index to conceptUri
        df = pd.merge(
            df, df_with_alt_label, how="left", on=["conceptUri", "altLabels"]
        ).set_index("conceptUri")

        # save DataFrame as json
        result = df.to_json(orient="index")

        result = json.loads(result)

        # split altLabelsPreprocessed into separate lists instead of separating labels by dots
        for key in result.keys():
            if result[key]["altLabelsPreprocessed"]:
                result[key]["altLabelsPreprocessed"] = split_list_by_dot(
                    result[key]["altLabelsPreprocessed"]
                )

        return result
