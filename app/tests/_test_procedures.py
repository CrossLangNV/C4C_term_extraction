import spacy
from app.terms import yield_terms

def extract_relations(sentence, nlp):
    d = dict()
    for p in sentence.split('.'):
        doc = nlp(p)
        term_list = yield_terms(doc)
        term_list = [term for term in term_list if not isinstance(term, spacy.tokens.token.Token)]
        for term in term_list:
            if any(token.pos_ == 'NOUN' and token.head.pos_ == 'VERB' and token.head.dep_ == 'ROOT' for token in term):
                if term.root.dep_ in d:
                    d.update({term.root.dep_ : max([d[term.root.dep_], term], key=len)})
                else:
                    d.update({term.root.dep_: term})
    return {y:x for x,y in d.items()}

nlp = spacy.load('en_core_web_md')
s = 'A high degree of transparency is essential to ensure that investors are adequately informed as to the true level of actual and potential transactions in bonds, structured finance products, emission allowances and derivatives irrespective of whether those transactions take place on regulated markets, multilateral trading facilities (MTFs), organised trading facilities, systematic internalisers, or outside those facilities. This high degree of transparency should also establish a level playing field between trading venues so that the price discovery process in respect of particular financial instruments is not impaired by the fragmentation of liquidity, and investors are not thereby penalised.'

r = extract_relations(s, nlp)
print(r)