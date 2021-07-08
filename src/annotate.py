from cassis.typesystem import load_typesystem
from cassis.xmi import load_cas_from_xmi
from cassis import Cas
import ahocorasick as ahc
from typing import Set, List

TYPESYSTEM = load_typesystem(open('typesystem.xml', 'rb'))
SOFA_ID = "html2textView"
VALUE_BETWEEN_TAG_TYPE = "com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType"
TERM_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.frequency.tfidf.type.Tfidf"
RELATION_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"
TAG_NAMES = "p"
PROCEDURES_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence"


def xmi2cas(input_xmi):
    cas = load_cas_from_xmi(input_xmi, typesystem=TYPESYSTEM, trusted=True)
    return cas


def extractTextTags(cas_view):
    for tag in cas_view.select(VALUE_BETWEEN_TAG_TYPE):
        yield tag


def annotateRelations(relations: dict, cas: Cas):
    cas_view = cas.get_view(SOFA_ID)
    Token = TYPESYSTEM.get_type(RELATION_TYPE)
    A = ahc.Automaton()
    for i, term in enumerate(relations.keys()):
        if not term.strip():
            continue
        A.add_word(term, (i, term))
    A.make_automaton()

    for tag in cas_view.select(VALUE_BETWEEN_TAG_TYPE):
        text = tag.get_covered_text()
        for end_index, (tfidf, term) in A.iter(text):
            if not term:
                continue
            start_index = end_index - (len(term) - 1)
            # print( start_index, end_index, term, text  )
            if is_token(start_index, end_index, text):
                cas_view.add_annotation(
                    Token(begin=tag.begin + start_index, end=tag.begin + end_index + 1, pos=relations[term],
                          id=term))


def annotateProcedures(procedures, begin_end_positions, cas):
    Sentence = TYPESYSTEM.get_type(PROCEDURES_TYPE)

    for procedure, begin_end_position in zip(procedures, begin_end_positions):
        cas.get_view(SOFA_ID).add_annotation(
            Sentence(begin=begin_end_position[0], end=begin_end_position[1], id="procedure"))


def annotateTerms(cas, terms_tf_idf):
    cas_view = cas.get_view(SOFA_ID)
    Token = TYPESYSTEM.get_type(TERM_TYPE)

    A = ahc.Automaton()
    for term in terms_tf_idf.keys():
        if not term.strip():
            continue
        A.add_word(term, (terms_tf_idf[term], term))
    A.make_automaton()

    for tag in cas_view.select(VALUE_BETWEEN_TAG_TYPE):
        text = tag.get_covered_text()
        for end_index, (tfidf, term) in A.iter(text):
            if not term:
                continue
            start_index = end_index - (len(term) - 1)
            # print( start_index, end_index, term, text  )
            if is_token(start_index, end_index, text):
                cas_view.add_annotation(
                    Token(begin=tag.begin + start_index, end=tag.begin + end_index + 1, tfidfValue=tfidf,
                          term=term))


"""
https://github.com/CrossLangNV/DGFISMA_definition_extraction/blob/9625b272dee22a8aa9fb929de73159bca93df845/utils.py#L8
"""


def get_sentences(cas: Cas):
    '''
    Given a cas, and a view (SofaID), this function selects all VALUE_BETWEEN_TAG_TYPE elements ( with tag.tagName in TAG_NAMES ), extracts the covered text, and returns the list of extracted sentences and a list of Tuples containing begin and end posistion of the extracted sentence in the sofa.
    Function will only extract text of the deepest child of the to be extracted tagnames.

    :param cas: cassis.typesystem.Typesystem. Corresponding Typesystem of the cas.
    :return: Tuple. Tuple with extracted text and the begin and end postion of the extracted text in the sofa.
    '''

    sentences = []
    begin_end_position = []
    for tag in cas.get_view(SOFA_ID).select(VALUE_BETWEEN_TAG_TYPE):
        if tag.tagName in set(TAG_NAMES) and deepest_child(cas, SOFA_ID, tag, TAG_NAMES,
                                                           VALUE_BETWEEN_TAG_TYPE):
            sentence = tag.get_covered_text().strip()
            if sentence:
                sentences.append(sentence)
                begin_end_position.append((tag.begin, tag.end))

    return sentences, begin_end_position


# helper function to check if a tag is nested or not
def deepest_child(cas: Cas, SofaID: str, tag, tagnames: Set[str] = set('p'), \
                  value_between_tagtype="com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType") -> bool:
    if len([item for item in cas.get_view(SofaID).select_covered(value_between_tagtype, tag) \
            if (item.tagName in tagnames and item.get_covered_text())]) > 1:
        return False
    else:
        return True


def is_token(start_index: int, end_index: int, text: str, special_characters: List[str] = ["-", "_", "+"]) -> bool:
    '''
    Given a start index, and end_index, and a string, this function checks if token(s) covered by the span is part of other token(s).

    :param start_index: int.
    :param end_index: int.
    :param special_characters: List. List of special characters treated as alpha characters
    :return: bool.
    '''

    if start_index < 0 or end_index < 0:
        raise ValueError(
            f"Both start_index and end_index should be >0, however start_index is {start_index} and end_index is {end_index}")

    elif end_index < start_index:
        raise ValueError(
            f"end_index should be > start_index, however start_index is {start_index} and end_index is {end_index}")

    elif end_index > (len(text) - 1):  # this one also takes care of no text case
        raise ValueError(
            f"end_index should be < len(text) -1, however end_index is {end_index} and len(text) is {len(text)}")

    # set of special characters treated as alpha characters
    # e.g.: the term 'livestock' in 'some livestock-some some' should not be annotated, but 'livestock' in 'some "livestock" some' should.
    special_characters = set(special_characters)

    # trivial case (start_index equal to end_index)
    # if start_index==end_index:
    # return False

    # e.g. 'livestock' in 'livestock'
    if start_index == 0 and end_index == len(text) - 1:
        return True

    # e.g. 'livestock' in 'livestock some'
    elif start_index == 0:
        if (text[end_index + 1].isalpha() or text[end_index + 1] in special_characters):
            return False

    # e.g. 'livestock' in 'some livestock'
    elif end_index == len(text) - 1:
        if (text[start_index - 1].isalpha() or text[start_index - 1] in special_characters):
            return False

    # e.g. 'livestock' in 'some livestock some';
    else:
        if (text[start_index - 1].isalpha() or text[start_index - 1] in special_characters) \
                or (text[end_index + 1].isalpha() or text[end_index + 1] in special_characters):
            return False

    return True
