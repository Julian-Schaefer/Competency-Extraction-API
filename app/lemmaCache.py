import pandas as pd
import spacy
import nltk
from nltk.corpus import wordnet
from HanTa import HanoverTagger as Ht
import os


__data_path__ = os.path.dirname(__file__) + "/lemma_cache_data"


def get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith("J"):
        return wordnet.ADJ
    elif treebank_tag.startswith("V"):
        return wordnet.VERB
    elif treebank_tag.startswith("N"):
        return wordnet.NOUN
    elif treebank_tag.startswith("R"):
        return wordnet.ADV
    else:
        return "n"


def split_into_sentences(text, language):
    return nltk.sent_tokenize(text, language=language)


def split_into_sentences_and_tokenize(text, language):
    sentences = nltk.sent_tokenize(text, language=language)
    tokenized_text = [
        nltk.word_tokenize(sentence[:-1], language=language)
        for sentence in sentences
    ]
    return tokenized_text


class LemmatizerGerman:
    def __init__(self):
        nltk.data.path.append(__data_path__ + "/nltk_data")
        self.nlp = spacy.load("de_core_news_sm", disable=["ner"])
        self.language = "german"
        self.morphys = pd.read_csv(
            __data_path__ + "/morphys.csv", encoding="utf-8", index_col=0
        )
        self.hannover_tagger = Ht.HanoverTagger(
            __data_path__ + "/morphmodel_ger.pgz"
        )

    def lemmatize_morphys(self, text):
        lemmatized_tokenized_text = []
        tokenized_sentences = split_into_sentences_and_tokenize(
            text, self.language
        )

        # loop over each tokenized sentence
        for sent in tokenized_sentences:
            lemmatized_sentence = []

            # loop over each token in the sentence
            for token in sent:
                try:
                    lemma = self.morphys.loc[token]["lemma"]
                except KeyError:
                    lemma = token
                lemmatized_sentence.append(lemma)

            lemmatized_tokenized_text.append(lemmatized_sentence)
        return lemmatized_tokenized_text

    def lemmatize_spacy(self, text):
        sentences = split_into_sentences(text, language=self.language)
        lemmatized_sentences = []
        for doc in self.nlp.pipe(sentences):
            for token in doc:
                lemmatized_sentences.append(token.lemma_)

        return lemmatized_sentences

    def lemmatize_hannover(self, text):
        tokenized_sentences = split_into_sentences_and_tokenize(
            text, language=self.language
        )
        lemmatized_sentences = []
        for sent in tokenized_sentences:
            lemmatized_sentences.append(
                [
                    x
                    for _, x, _ in self.hannover_tagger.tag_sent(
                        sent, taglevel=1
                    )
                ]
            )
        return lemmatized_sentences


class LemmatizerEnglish:
    def __init__(self):
        self.language = "english"
        self.nlp = spacy.load("en_core_web_sm", disable=["ner"])
        nltk.data.path.append(__data_path__ + "/nltk_data")
        self.nltk_lemmatizer = nltk.stem.WordNetLemmatizer()

    def lemmatize_spacy(self, text):
        sentences = split_into_sentences(text, language=self.language)
        lemmatized_sentences = []
        for doc in self.nlp.pipe(sentences):
            lemmatized_sentences.append([token.lemma_ for token in doc[:-1]])
        return lemmatized_sentences

    def lemmatize_nltk(self, text):
        tokenized_sentences = split_into_sentences_and_tokenize(
            text, self.language
        )
        lemmatized_sentences = []
        for sentence in tokenized_sentences:
            lemmatized_sentence = []
            tagged_sentence = nltk.pos_tag(sentence)
            for token, tag in tagged_sentence:
                lemmatized_sentence.append(
                    self.nltk_lemmatizer.lemmatize(token, get_wordnet_pos(tag))
                )
            lemmatized_sentences.append(lemmatized_sentence)
        return lemmatized_sentences
