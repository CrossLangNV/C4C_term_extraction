import spacy
from terms import yield_terms, clean_non_category_words, term_length_is_conform


def launch_relation_extraction(sentences, nlp, max_len_ngram):
    for s in sentences:
        yield extract_relations(s, nlp, max_len_ngram)


def extract_relations(sentence, nlp, max_len_ngram):
    d = dict()
    for p in sentence.split('.'):
        doc = nlp(p)
        term_list = yield_terms(doc)
        term_list = [term for term in term_list if not isinstance(term, spacy.tokens.token.Token)]
        for term in term_list:
            if any(token.pos_ == 'NOUN' and token.head.pos_ == 'VERB' and token.head.dep_ == 'ROOT' for token in term):
                ngram = clean_non_category_words(term)  # will return empty strings sometimes
                if term_length_is_conform(ngram, max_len_ngram):
                    if term.root.dep_ in d:
                        d.update({term.root.dep_: max([d[term.root.dep_], term], key=len)})
                    else:
                        d.update({term.root.dep_: term})
    return {y: x for x, y in d.items()}


def parse_procedures(procedures):
    d = dict()
    phone = []
    emails = []
    hours = []

    for p in procedures:
        p = p.strip()
        if '+' in p:
            phone.append(p)

        if '@' in p:
            emails.append(p)

        if 'Uhr' in p:
            hours.append(p)

    d.update({'phone': phone})
    d.update({'emails': emails})
    d.update({'opening_hours': hours})
    # d.update({'description' : description})
    return d
