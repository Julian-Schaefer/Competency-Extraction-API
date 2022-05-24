import pandas as pd
import spacy
import nltk
from nltk.corpus import wordnet
from HanTa import HanoverTagger as Ht
import os


__data_path__ = os.path.dirname(__file__) + r"\lemma_cache_data"


def split_into_sentences(text, language):
    return nltk.sent_tokenize(text, language=language)


def split_into_sentences_and_tokenize(text, language):
    sentences = nltk.sent_tokenize(text, language=language)
    tokenized_text = [nltk.word_tokenize(sentence[:-1], language=language) for sentence in sentences]
    return tokenized_text


def lowercase_course_descr(course_descr: str):
    """
    :param course_descr: A course description
    :type course_descr: str
    :return: The lowercased course description
    :rtype: str
    """
    return str.lower(course_descr)


class LemmatizerGerman:
    def __init__(self):
        nltk.data.path.append(__data_path__ + r"\nltk_data")
        self.morphys = pd.read_csv(__data_path__ + r"\morphys.csv", encoding="utf-8", index_col=0)
        self.nlp = spacy.load("de_core_news_sm", disable=['ner'])
        self.language = "german"
        self.hannover_tagger = Ht.HanoverTagger(__data_path__ + r"\morphmodel_ger.pgz")
        with open(__data_path__ + r"\stopwords-de.txt", "r", encoding="utf-8") as f:
            self.stopwords = list(map(str.strip, list(f)))

    def remove_stopwords_from_course_descr(self, course_descr):
        pass

    def lemmatize_morphys(self, text):
        lemmatized_tokenized_text = []
        tokenized_sentences = split_into_sentences_and_tokenize(text, self.language)

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
            lemmatized_sentences.append([token.lemma_ for token in doc[:-1]])

        return lemmatized_sentences

    def lemmatize_hannover(self, text):
        tokenized_sentences = split_into_sentences_and_tokenize(text, language=self.language)
        lemmatized_sentences = []
        for sent in tokenized_sentences:
            lemmatized_sentences.append([x for _, x, _ in self.hannover_tagger.tag_sent(sent, taglevel=1)])
        return lemmatized_sentences


class LemmatizerEnglish:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm", disable=['ner'])
        self.language = "english"
        nltk.data.path.append(__data_path__ + r"\nltk_data")
        self.nltk_lemmatizer = nltk.stem.WordNetLemmatizer()

    def lemmatize_spacy(self, text):
        sentences = split_into_sentences(text, language=self.language)
        lemmatized_sentences = []
        for doc in self.nlp.pipe(sentences):
            lemmatized_sentences.append([token.lemma_ for token in doc[:-1]])
        return lemmatized_sentences

    def lemmatize_nltk(self, text):
        tokenized_sentences = split_into_sentences_and_tokenize(text, self.language)
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


# lemmazier_de = LemmatizerGerman()
# print(lemmazier_de.lemmatize_morphys("Hallo mein Name ist Amir. ich komme aus Berlin und war heute essen"))


