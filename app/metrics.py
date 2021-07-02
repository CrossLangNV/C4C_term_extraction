from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from typing import List, Dict
import operator

def calculate_frequency(corpus: List, list_of_terms: List, max_ngram_len: int) -> List:
    """
    :param corpus: list of sentences
    :param list_of_terms: list of ngrams
    :param max_ngram_len: maximal ngram length
    :return:
    """

    vectorizer = CountVectorizer(vocabulary=list_of_terms, ngram_range=(1, max_ngram_len), lowercase=False)
    tf = vectorizer.transform(corpus)
    word_list = vectorizer.get_feature_names()
    count_list = tf.toarray().sum(axis=0)
    terms_and_counts = list(zip(word_list, count_list))
    return terms_and_counts


def calculate_tf_idf(corpus: List, list_of_terms: List, max_ngram_len: int) -> Dict:
    """
    :param max_ngram_len: maximal ngram length
    :param corpus: a list of text segments
    :param list_of_terms: a list of terms
    :return: {term : tf-idf}
    """

    vectorizer = TfidfVectorizer(vocabulary=list_of_terms, ngram_range=(1, max_ngram_len + 1), sublinear_tf=True)
    vectorizer.fit_transform(corpus)
    terms_n_tfidf = {}
    for term, score in zip(vectorizer.get_feature_names(), vectorizer.idf_):
        terms_n_tfidf.update({term: score})

    terms_n_tfidf = dict(sorted(terms_n_tfidf.items(), key=operator.itemgetter(1), reverse=True))

    return terms_n_tfidf
