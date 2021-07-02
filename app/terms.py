import string
import spacy
import language_tool_python
from typing import List, Tuple

#test

INVALID_POS_TAGS = ['DET', 'PUNCT', 'ADP', 'CCONJ', 'SYM', 'NUM', 'PRON', 'SCONJ', 'ADV']
PUNCTUATION_AND_DIGITS = string.punctuation.replace('-', '0123456789').replace('\'', '')

def extractAbbvTerm(tokens, t, sw):
    """

    :param tokens: list of tokens
    :param t: the to be mapped abbreviation
    :param sw: list of stopwords
    :return:
    """
    i = tokens.index(t)
    if i - 10 > 0:
        start = i - 10
    else:
        start = 0
    if i + 10 < len(tokens):
        end = i + 10
    else:
        end = len(tokens) - 1

    l = tokens[start:end]
    candidates = set()
    for i, x in enumerate(l):
        slice = l[i: i + len(t)]
        letters = t.lower()
        if t in slice:
            slice.remove(t)
        for x in slice:
            first_letter = x[0].lower()
            if x != t and first_letter in letters:
                letters = letters.replace(first_letter, '')

            slice = [x for x in slice if x not in sw and x[0].lower() in t.lower()]
            if len(slice) > len(t) * 0.65:
                candidates.add(' '.join(slice).strip())
    if candidates:
        return max(candidates, key=len)



def extractAbbv(doc, sw) -> List[Tuple[str, str]]:
    '''

    :param doc: SpaCy object Doc
    :param sw: list of stopwords
    :return: A List of Tuples containing abbreviations.
    '''

    tokens = [t.text for t in doc]
    res = []
    for t in tokens:
        prop = sum(1 for c in t if c.isupper()) / len(t)
        if (prop > 0.5
                and 1 < len(t) < 6
                and t.lower() not in sw
                and t.isalpha()):
            term = extractAbbvTerm(tokens, t, sw)
            if (term is not None):
                res.append((t, term))
    abvs = []
    for x in list(set(res)):
        abvs.append((x[0].strip(), x[1].strip()))

    return abvs


def clean_non_category_words_back(ngram):
    """

    :param ngram: SpaCy span object
    :return: rectified SpaCy span object

    This function is for cleaning ngrams such as 'decision with which' / 'decision which' / 'decision as from which'
    """
    if ngram[-1].pos_ in INVALID_POS_TAGS:
        return clean_non_category_words_back(ngram[:-1])
    else:
        return ngram


def clean_non_category_words_front(ngram):
    """

    :param ngram: SpaCy span object
    :return: rectified SpaCy span object

    This function is for cleaning ngrams such as 'of the decision' / 'the decision' / 'as of the decision'
    """
    if ngram[0].pos_ in INVALID_POS_TAGS:
        return clean_non_category_words_front(ngram[1:])
    else:
        return ngram


def clean_non_category_words(ngram):
    """

    :param ngram:  SpaCy span object
    :return: rectified SpaCy span object
    """
    clean_front_ngram = clean_non_category_words_front(ngram)
    if clean_front_ngram is not None:
        clean_ngram = clean_non_category_words_back(clean_front_ngram)
        return clean_ngram


def yield_terms(doc):
    """

    :param doc: SpaCy Doc object
    :return: yields various noun phrases

    Here we rely on the dependency parser, each noun or pronoun is the root of a noun phrase tree, e.g.:
    "I've just watched 'Eternal Sunshine of the Spotless Mind' and found it corny"

    We iterate over each branch of the tree and yield the Doc spans that contain:
        1. the root : 'sunshine'
        2. left branch + the root : 'eternal sunshine'
        3. the root + right branch : 'sunshine of the spotless mind'
        4. left branch + the root + right branch : 'eternal sunshine of the spotless mind'

    """
    for token in doc:
        if token.pos_ == ('NOUN' or 'PROPN'):
            yield doc[token.i]
            yield doc[token.i:token.right_edge.i + 1]
            yield doc[token.left_edge.i:token.right_edge.i + 1]
            yield doc[token.left_edge.i: token.i + 1]


def term_text_is_clean(noun_phrase):
    """

    :param noun_phrase: SpaCy token or span, noun phrase of any length
    :return: True or False
    """
    if noun_phrase.text.isascii() and all(
            not character in PUNCTUATION_AND_DIGITS for character in noun_phrase.text.strip()):
        return True
    else:
        return False


def term_does_not_contain_stopwords(noun_phrase, STOP_WORDS):
    """

    :param noun_phrase: SpaCy span
    :param STOP_WORDS: set of stop words per language
    :return: True or False
    """
    if not any(word.text in STOP_WORDS for word in noun_phrase):
        return True
    else:
        return False


def term_length_is_conform(term, max_len_ngram):
    """

    :param term: SpaCy span object
    :param max_len_ngram: int
    :return: True or False
    """
    if max_len_ngram >= len(term) > 0:
        return True
    else:
        return False


def filter_terms(terms, language_code):
    """

    :param terms: list of terms
    :param language_code: 'DE' / 'FR' / etc.
    :return: 
    """
    if language_code == 'DE':
        terms = [term for term in terms if term[0].isupper()]
    else:
        terms = [term.lower() for term in terms]
    tool = language_tool_python.LanguageTool(language_code)
    final_terms = set()
    for x in terms:
        m = tool.check(x.capitalize())
        if not m:
            final_terms.add(x)
    return final_terms


def extract_terms(corpus, max_len_ngram, nlp, stop_words=None):
    """
    :param corpus: list of documents
    :param max_len_ngram: int
    :param nlp: the SpaCy model
    :param stop_words: list of blacklisted words per language
    :return: list of terms
    """
    for page in corpus:
        doc = nlp(page)
        term_list = yield_terms(doc)
        for term in term_list:
            if term_text_is_clean(term):
                if isinstance(term, spacy.tokens.token.Token):
                    yield term.text.lower()
                    yield term.lemma_
                else:
                    ngram = clean_non_category_words(term)  # will sometimes return empty strings
                    if ngram:
                        conditions = [term_length_is_conform(ngram, max_len_ngram)]

                        if stop_words:
                            condition_two = term_does_not_contain_stopwords(ngram, stop_words)
                            conditions.append(condition_two)

                        if all(conditions):
                            yield ' '.join([word.lemma_ for word in ngram]).strip()
                            yield ngram.text.strip()
            else:
                continue
