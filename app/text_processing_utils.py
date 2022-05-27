import string
import pandas as pd
import spacy
import nltk
from nltk.corpus import wordnet
from HanTa import HanoverTagger as Ht
import os
from typing import List
from pandas import DataFrame


__data_path__ = os.path.dirname(__file__) + r"\lemma_cache_data"


def add_nltk_data_path():
    """
    Adds the directory ".\app\nltk_data" to the list of paths that the nltk library searches in for valid nltk models.
    """
    if not __data_path__ + r"\nltk_data" in nltk.data.path:
        nltk.data.path.append(__data_path__ + r"\nltk_data")


def split_course_descr_into_sentences(course_descr: str, language: str) -> List[str]:
    """
    Splits a course description into sentences using the nltk Punkt Sentence Tokenizer.
    :param course_descr: A course description
    :type course_descr: str
    :param language: The language of the course description; "english" or "german"
    :type language: str
    :return: A list of sentences
    :rtype: List[str]
    """
    add_nltk_data_path()
    return nltk.sent_tokenize(course_descr, language=language)


def tokenize_sentences(sentences: List[str], language: str) -> List[List[str]]:
    """
    Tokenizes a list of sentences using the nltk Tokenizer.
    :param sentences: A list of sentences
    :type sentences: List[str]
    :param language: The language of the sentences; "english" or "german"
    :return: A list of tokenized sentences
    :rtype: List[List[str]]
    """
    add_nltk_data_path()
    tokenized_text = [nltk.word_tokenize(sentence, language=language) for sentence in sentences]
    return tokenized_text


def remove_punctuation_from_tokenized_sentences(tokenized_sentences: List[List[str]]) -> List[List[str]]:
    """
    Removes punctuation from a list of tokenized sentences. If a token only contains punctuation,
    it is removed entirely. Hyphens are only removed if they appear at the start or the end of the token.
    For example the hyphen in the token "H-Milch" will not be removed.
    :param tokenized_sentences: A list of tokenized sentences
    :type tokenized_sentences: List[List[str]]
    :return: The list of tokenized sentences with punctuation removed
    :rtype: List[List[str]]
    """
    tokenized_sentences_without_punctuation = []
    punct = string.punctuation.replace("-", "")
    # remove punctuation except for hyphens
    for sentence in tokenized_sentences:
        tokenized_sentences_without_punctuation.append(
            [token.translate(str.maketrans('', '', punct)) for token in sentence
             if token.translate(str.maketrans('', '', punct)) != ""]
        )
    # remove hyphens that appear at the start or the end of the token
    tokenized_sentences_without_punctuation_and_hyphens = []
    for sentence in tokenized_sentences_without_punctuation:
        tokenized_sentences_without_punctuation_and_hyphens.append(
            [token.strip("-") for token in sentence if token.strip("-") != ""]
        )
    return tokenized_sentences_without_punctuation_and_hyphens


def remove_numeric_tokens(tokenized_sentences: List[List[str]]) -> List[List[str]]:
    """
    Removes numeric tokens from a list of tokenized sentences.
    :param tokenized_sentences: A list of tokenized sentences
    :type tokenized_sentences: List[List[str]]
    :return: The list of tokenized sentences with numeric tokens removed
    :rtype: List[List[str]]
    """
    tokenized_sentences_without_numeric_tokens = []
    for sentence in tokenized_sentences:
        tokenized_sentences_without_numeric_tokens.append(
            [token for token in sentence if not token.isnumeric()]
        )
    return tokenized_sentences_without_numeric_tokens


def lowercase_tokenized_sentences(tokenized_sentences: List[List[str]]) -> List[List[str]]:
    """
    :param tokenized_sentences: A list of tokenized sentences
    :type tokenized_sentences: List[List[str]]
    :return: The lowercased course description
    :rtype: List[List[str]]
    """
    lowercased_tokenized_sentences = []
    for sentence in tokenized_sentences:
        lowercased_tokenized_sentences.append(
            [str.lower(token) for token in sentence]
        )
    return lowercased_tokenized_sentences


class TextProcessorGerman:
    """
    This class is provides an interface for processing course descriptions before parsing them
    into the entitiy recognition algorithm
    :param morphys: The morphys look up table for german words and their respective lemmas
    :type morphys: DataFrame
    :param nlp: The pretrained spacy "de_core_news_sm" model for the German language
    :type nlp: spacy.lang.de.German
    :param language: The language that the TextProcessor is compatible for
    :type language: str
    :param hannover_tagger: The Hannover Tagger from the Hanta library which provides a pretrained nlp model
    for the German language
    :type hannover_tagger: HanTa.HanoverTagger.HanoverTagger
    :param stopwords: A list of German stopwords. The stopwords were stored from the following git repo
    https://github.com/stopwords-iso/stopwords-de
    """
    def __init__(self):
        add_nltk_data_path()
        self.morphys = pd.read_csv(__data_path__ + r"\morphys.csv", encoding="utf-8", index_col=0)
        self.nlp = spacy.load("de_core_news_sm", disable=['ner'])
        self.language = "german"
        self.hannover_tagger = Ht.HanoverTagger(__data_path__ + r"\morphmodel_ger.pgz")
        with open(__data_path__ + r"\stopwords-de.txt", "r", encoding="utf-8") as f:
            self.stopwords = list(map(str.strip, list(f)))

    def remove_stopwords_from_tokenized_sentences(self, tokenized_sentences: List[List[str]]):
        """
        Remove stop words from a list of tokenized sentences.
        Each token is iterated through and removed if it exists in the list of stopwords.
        The look up algorithm is not case sensitive. If a stopword appears in upper case, it will still be removed.
        :param tokenized_sentences: A list of tokenized sentences
        :type tokenized_sentences: List[List[str]]
        :return: The list of tokenized sentences without stopwords
        :rtype: List[List[str]]
        """
        tokenized_sentences_without_stopwords = []
        for sentence in tokenized_sentences:
            tokenized_sentences_without_stopwords.append(
                [token for token in sentence if token.lower() not in self.stopwords]
            )
        return tokenized_sentences_without_stopwords

    def lemmatize_morphys(self, tokenized_sentences: List[List[str]]) -> List[List[str]]:
        """
        Lemmatize a list of tokenized sentences using the morphys look up table.
        If a lemma for a token is not found in the table and the token represents a hyphen-separated compound,
        the compound is separated and the lemma for each individual word is looked up instead.
        The individual lemmas are then joined back together using hyphens.
        For example the compound "Personen-gegessen" becomes "Person-essen".
        Only the morphys lemmatizer provides this functionality as it used first in the general lemmatizer method.
        :param tokenized_sentences: A list of tokenized sentences
        :type tokenized_sentences: List[List[str]]
        :return: The list of tokenized sentences where each token is lemmatized
        :rtype: List[List[str]]
        """
        df = self.morphys
        lemmatized_tokenized_sentences = []
        # loop over each tokenized sentence
        i = 1
        for sent in tokenized_sentences:
            print(i, " / ", len(tokenized_sentences))
            lemmatized_sentence = []
            i += 1
            # loop over each token in the sentence
            for token in sent:
                # try to find the token
                try:
                    lemma = df[df["form"] == token]["lemma"].tolist()[0]
                except IndexError:
                    # if it does not find the token, check if it is a hyphen separated compound
                    if "-" in token:
                        # if yes, split the compound, lemmatize each component separately and join the
                        # individual lemmas back together using hyphens
                        token = token.split("-")
                        lemma = []
                        for x in token:
                            try:
                                lemma.append(df[df["form"] == x]["lemma"].tolist()[0])
                            except IndexError:
                                lemma.append(x)
                        lemma = "-".join(lemma)
                    else:
                        # if not just use the token itself as the lemma
                        lemma = token
                lemmatized_sentence.append(lemma)

            lemmatized_tokenized_sentences.append(lemmatized_sentence)
        return lemmatized_tokenized_sentences

    def lemmatize_spacy(self, tokenized_sentences):
        """
        Lemmatize a list of tokenized sentences using the spacy pretrained "de_core_news_sm" model.
        :param tokenized_sentences: A list of tokenized sentences
        :type tokenized_sentences: List[List[str]]
        :return: The list of tokenized sentences where each token is lemmatized
        :rtype: List[List[str]]
        """
        lemmatized_sentences = []
        for sentence in tokenized_sentences:
            lemmatized_sentences.append(
                [self.nlp(token)[0].lemma_ for token in sentence]
            )
        return lemmatized_sentences

    def lemmatize_hannover(self, tokenized_sentences):
        """
        Lemmatize a list of tokenized sentences using the pretrained "Hannover Tagger" model.
        :param tokenized_sentences: A list of tokenized sentences
        :type tokenized_sentences: List[List[str]]
        :return: The list of tokenized sentences where each token is lemmatized
        :rtype: List[List[str]]
        """
        lemmatized_sentences = []
        for sent in tokenized_sentences:
            lemmatized_sentences.append([x for _, x, _ in self.hannover_tagger.tag_sent(sent, taglevel=1)])
        return lemmatized_sentences

    def lemmatize(self, tokenized_sentences):
        """
        Lemmatize a list of tokenized sentences first using the morphys lemmatizer then the spacy lemmatizer and
        finally the hannover lemmatizer.
        :param tokenized_sentences: A list of tokenized sentences
        :type tokenized_sentences: List[List[str]]
        :return: The list of tokenized sentences where each token is lemmatized
        :rtype: List[List[str]]
        """
        tokenized_sentences = self.lemmatize_morphys(tokenized_sentences)
        tokenized_sentences = self.lemmatize_spacy(tokenized_sentences)
        tokenized_sentences = self.lemmatize_hannover(tokenized_sentences)
        return tokenized_sentences

    def preprocess_course_description(self, course_descr: str) -> List[List[str]]:
        """
        Preprocess a course description before parsing it into the entity recognition algorithm.
        This method represents a wrapper for all methods and functions in this module.
        The course descriptions are preprocessed in the following order:
        - split into sentences
        - tokenize each sentence
        - remove punctuation
        - remove numeric tokens
        - remove stopwords
        - lemmatize using the morphys lemmatizer
        - lemmatize using the spacy lemmatizer
        - lemmatize using the hannover lemmatizer
        - lowercase each token
        :param course_descr: A course description
        :type course_descr: str
        :return: The preprocessed course description
        :rtype: List[List[str]]
        """
        text = split_course_descr_into_sentences(course_descr, self.language)
        text = tokenize_sentences(text, self.language)
        text = remove_punctuation_from_tokenized_sentences(text)
        text = remove_numeric_tokens(text)
        text = self.remove_stopwords_from_tokenized_sentences(text)
        text = self.lemmatize_morphys(text)
        # text = self.lemmatize(text)
        text = lowercase_tokenized_sentences(text)
        return text


class LemmatizerEnglish:
    def __init__(self):
        add_nltk_data_path()
        self.nlp = spacy.load("en_core_web_sm", disable=['ner'])
        self.language = "english"
        self.nltk_lemmatizer = nltk.stem.WordNetLemmatizer()

    def lemmatize_spacy(self, text):
        sentences = split_course_descr_into_sentences(text, language=self.language)
        lemmatized_sentences = []
        for doc in self.nlp.pipe(sentences):
            lemmatized_sentences.append([token.lemma_ for token in doc[:-1]])
        return lemmatized_sentences

    def lemmatize_nltk(self, text):
        sentences = split_course_descr_into_sentences(text, self.language)
        tokenized_sentences = tokenize_sentences(sentences, self.language)
        lemmatized_sentences = []
        for sentence in tokenized_sentences:
            lemmatized_sentence = []
            tagged_sentence = nltk.pos_tag(sentence)
            for token, tag in tagged_sentence:
                # convert tag into wordnet compatible tag
                if tag.startswith('J'):
                    tag = wordnet.ADJ
                elif tag.startswith('V'):
                    tag = wordnet.VERB
                elif tag.startswith('N'):
                    tag = wordnet.NOUN
                elif tag.startswith('R'):
                    tag = wordnet.ADV
                else:
                    tag = "n"

                lemmatized_sentence.append(self.nltk_lemmatizer.lemmatize(token, tag))
            lemmatized_sentences.append(lemmatized_sentence)
        return lemmatized_sentences
