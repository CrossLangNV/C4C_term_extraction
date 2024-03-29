#https://github.com/explosion/spaCy/blob/f22704621ef5d136e00a47068288bf55f666716d/spacy/tests/conftest.py#L70
#https://stackoverflow.com/questions/56728218/how-to-mock-spacy-models-doc-objects-for-unit-tests
import pytest

from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy.util import get_lang_class

from src.terms.terms import TermExtractor

from .util import get_doc

@pytest.fixture()
def en_vocab():
    return get_lang_class("en").Defaults.create_vocab()

@pytest.fixture()
def doc_example_1( en_vocab ):
    words="Credit and mortgage account holders of the rich must submit their requests".split()
    pos=['NOUN', 'CCONJ', 'NOUN', 'NOUN', 'NOUN', 'ADP', 'DET', 'ADJ', 'VERB', 'VERB', 'DET', 'NOUN']
    heads=[3, -1, -2, 1, 5, -1, 1, -2, 1, 0, 1, -2]
    doc=get_doc( en_vocab, words=words, pos=pos, heads=heads )
    return doc

@pytest.fixture()
def doc_example_2( en_vocab ):
    words="This is a test sentence the 12 test sentence 23 27".split()
    pos=['DET','AUX','DET','NOUN','NOUN','DET','NUM','NOUN','NOUN','NUM','NUM']
    heads=[1, 0, 2, 1, -3, 3, 2, 1, -4, 1, -2]
    doc=get_doc( en_vocab, words=words, pos=pos, heads=heads )
    return doc

@pytest.fixture()
def doc_example_3( en_vocab ):
    words="Credit and mortgage account holders of the rich must submit their requests . They live in the City Of Monaco near Nice .".split()
    pos=['NOUN','CCONJ','NOUN','NOUN','NOUN','ADP','DET','ADJ','VERB','VERB','DET','NOUN','PUNCT','PRON','VERB','ADP','DET','PROPN','ADP','PROPN','SCONJ','PROPN','PUNCT']    
    heads=[3, -1, -2, 1, 5, -1, 1, -2, 1, 0, 1, -2, -3, 1, 0, -1, 1, -2, -1, -1, -6, -1, -8]
    ents=[(16, 20, 384), (21, 22, 384)]
    doc=get_doc( en_vocab, words=words, pos=pos, heads=heads, ents=ents )
    return doc

@pytest.fixture()
def doc_example_empty_doc( en_vocab ):
    words="".split()
    pos=[]
    heads=[]
    doc=get_doc( en_vocab, words=words, pos=pos, heads=heads )
    return doc


def test_get_terms_ner_en():
    '''
    test .get_terms_ner method of TermExtractor class. We use pretrained Spacy model (EN, en_core_web_lg ) in this test. So test can fail if other Spacy models are loaded than the ones this test was written with
    '''
    
    sentences=\
    [ "This is a test sentence the 12 test sentence 23 27 " ,
      "test sentence",
      "I've just watched the 'Eternal Sunshine of the Spotless Mind' and found it corny" ,
      "Credit and mortgage account holders of the rich must submit their requests",
      "123",
      "" ]
    
    #initialize a TermExtractor object.
    termextractor=TermExtractor( languages=[ 'en' ], max_ngram=10, remove_stopwords=True , use_spellcheck_tool=False  )
    pred_terms,pred_ners=termextractor.get_terms_ner( sentences, language='en' )
    
    true_terms= \
    [('test', 'test'),
     ('sentence', 'sentence'),
     ('test sentence', 'test sentence'),
     ('Sunshine', 'Sunshine'),
     ('Sunshine of the Spotless Mind', 'Sunshine of the Spotless Mind'),
     ('Eternal Sunshine of the Spotless Mind','eternal Sunshine of the Spotless Mind'),
     ('Eternal Sunshine', 'eternal Sunshine'),
     ('Spotless', 'Spotless'),
     ('Mind', 'Mind'),
     ('Spotless Mind', 'Spotless Mind'),
     ('Credit', 'credit'),
     ('Credit and mortgage', 'credit and mortgage'),
     ('mortgage', 'mortgage'),
     ('account', 'account'),
     ('Credit and mortgage account', 'credit and mortgage account'),
     ('holders', 'holder'),
     ('holders of the rich', 'holder of the rich'),
     ('Credit and mortgage account holders of the rich', 'credit and mortgage account holder of the rich'),
     ('Credit and mortgage account holders', 'credit and mortgage account holder'),
     ('requests', 'request')]
    
    true_ners=\
    [[('12', 'CARDINAL', 28, 30), ('23 27', 'PERCENT', 45, 50)],
     [],
     [("the 'Eternal Sunshine of the Spotless Mind'", 'WORK_OF_ART', 18, 61)],
     [],
     [('123', 'CARDINAL', 0, 3)],
     []]
    
    assert true_terms == pred_terms
    assert true_ners == pred_ners
    
    
def test_get_terms_ner_de():
    '''
    test .get_terms_ner method of TermExtractor class. We use pretrained Spacy model (DE, de_core_news_lg) in this test. So test can fail if other Spacy models are loaded than the ones this test was written with
    '''
    
    sentences=[ 'Kredit-und Hypothekenkontoinhaber der Reichen müssen ihre Anträge stellen' ]
    
    #initialize a TermExtractor object.
    termextractor=TermExtractor( languages=[ 'de' ], max_ngram=10, remove_stopwords=True , use_spellcheck_tool=False  )
    pred_terms,pred_ners=termextractor.get_terms_ner( sentences, language='de' )
    
    true_terms= \
    [('Kredit-und', 'Kredit-und'), #this could be improved
     ('Hypothekenkontoinhaber', 'Hypothekenkontoinhaber'),
     ('Hypothekenkontoinhaber der Reichen', 'Hypothekenkontoinhaber der Reiche'),
     ('Kredit-und Hypothekenkontoinhaber der Reichen','Kredit-und Hypothekenkontoinhaber der Reiche'),
     ('Kredit-und Hypothekenkontoinhaber', 'Kredit-und Hypothekenkontoinhaber'),
     ('Reichen', 'Reiche')]
    
    true_ners=\
    [[('Kredit-und', 'PER', 0, 10)]]
    
    assert true_terms==pred_terms
    assert true_ners==pred_ners
    

def test_parse_doc_1( doc_example_1 ):
    
    '''
    test _parse_doc method of TermExtractor class.
    '''
    
    assert type( doc_example_1 ) == Doc
    
    #load an empty TermExtractor ( i.e. without 'any' 'languages' )
    termextractor=TermExtractor( languages=[] )
    
    terms=termextractor._parse_doc( doc_example_1 )
    
    terms_text_pred=[ term.text for term in terms ]

    terms_true= \
    ['Credit',
     'Credit and mortgage',
     'Credit and mortgage',
     'Credit',
     'mortgage',
     'mortgage',
     'mortgage',
     'mortgage',
     'account',
     'account',
     'Credit and mortgage account',
     'Credit and mortgage account',
     'holders',
     'holders of the rich',
     'Credit and mortgage account holders of the rich',
     'Credit and mortgage account holders',
     'requests',
     'requests',
     'their requests',
     'their requests']
    
    assert terms_true == terms_text_pred
    
    
def test_parse_doc_2( doc_example_2 ):
    
    '''
    test _parse_doc method of TermExtractor class.
    '''

    assert type( doc_example_2 ) == Doc
    
    #load an empty TermExtractor ( i.e. without 'any' 'languages' )
    termextractor=TermExtractor( languages=[] )
    
    terms=termextractor._parse_doc( doc_example_2 )
    
    terms_text_pred=[ term.text for term in terms ]

    terms_true= \
    ['test',
     'test',
     'test',
     'test',
     'sentence',
     'sentence the 12 test sentence 23 27',
     'a test sentence the 12 test sentence 23 27',
     'a test sentence',
     'test',
     'test',
     'test',
     'test',
     'sentence',
     'sentence 23 27',
     'the 12 test sentence 23 27',
     'the 12 test sentence']
    
    assert terms_true == terms_text_pred
    
    
def test_parse_doc_3( doc_example_3 ):
    
    '''
    test _parse_doc method of TermExtractor class.
    '''

    assert type( doc_example_3 ) == Doc
    
    #load an empty TermExtractor ( i.e. without 'any' 'languages' )
    termextractor=TermExtractor( languages=[] )
    
    terms=termextractor._parse_doc( doc_example_3 )
    
    terms_text_pred=[ term.text for term in terms ]

    terms_true= \
    ['Credit',
     'Credit and mortgage',
     'Credit and mortgage',
     'Credit',
     'mortgage',
     'mortgage',
     'mortgage',
     'mortgage',
     'account',
     'account',
     'Credit and mortgage account',
     'Credit and mortgage account',
     'holders',
     'holders of the rich',
     'Credit and mortgage account holders of the rich',
     'Credit and mortgage account holders',
     'requests',
     'requests',
     'their requests',
     'their requests',
     'City',
     'City Of Monaco',
     'the City Of Monaco',
     'the City',
     'Monaco',
     'Monaco',
     'Monaco',
     'Monaco',
     'Nice',
     'Nice',
     'Nice',
     'Nice']
    
    assert terms_true == terms_text_pred
    
    
def test_parse_empty_doc( doc_example_empty_doc ):
    
    '''
    test _parse_doc method of TermExtractor class.
    '''

    assert type( doc_example_empty_doc  ) == Doc
    
    #load an empty TermExtractor ( i.e. without 'any' 'languages' )
    termextractor=TermExtractor( languages=[] )
    
    terms=termextractor._parse_doc( doc_example_empty_doc )
    
    terms_text_pred=[ term.text for term in terms ]

    terms_true= []
    
    assert terms_true == terms_text_pred
    

def test_ner_doc_1( doc_example_1 ):
    
    '''
    test _ner_doc method of TermExtractor class
    '''
    
    assert type( doc_example_1  ) == Doc
    
    #load an empty TermExtractor ( i.e. without 'any' 'languages' )
    termextractor=TermExtractor( languages=[] )
    
    ners_pred=termextractor._ner_doc( doc_example_1 )
    
    ners_true=[]
    
    assert ners_pred == ners_true
    
    
def test_ner_doc_2( doc_example_2 ):
    
    '''
    test _ner_doc method of TermExtractor class
    '''
    
    assert type( doc_example_2  ) == Doc
    
    #load an empty TermExtractor ( i.e. without 'any' 'languages' )
    termextractor=TermExtractor( languages=[] )
    
    ners_pred=termextractor._ner_doc( doc_example_2 )
    
    ners_true=[]
    
    assert ners_pred == ners_true
    
    
def test_ner_doc_3( doc_example_3 ):
    
    '''
    test _ner_doc method of TermExtractor class
    '''
    
    assert type( doc_example_3  ) == Doc
    
    #load an empty TermExtractor ( i.e. without 'any' 'languages' )
    termextractor=TermExtractor( languages=[] )
    
    ners_pred=termextractor._ner_doc( doc_example_3 )
    
    ners_true=[('the City Of Monaco', 'GPE', 90, 108), ('Nice', 'GPE', 114, 118)] 
    
    assert ners_pred == ners_true
    
    
def test_ner_doc_empty_doc( doc_example_empty_doc ):
    
    '''
    test _ner_doc method of TermExtractor class
    '''
    
    assert type( doc_example_empty_doc ) == Doc
    
    #load an empty TermExtractor ( i.e. without 'any' 'languages' )
    termextractor=TermExtractor( languages=[] )
    
    ners_pred=termextractor._ner_doc( doc_example_empty_doc )
    
    ners_true=[]
    
    assert ners_pred == ners_true
    
    
def test_term_list_is_unique( doc_example_1 ):
    
    '''
    test _make_term_list_unique method of TermExtractor class.
    '''

    assert type( doc_example_1  ) == Doc
    
    #make term list with duplicates at .text level of Span objects:
    term_list=[doc_example_1[0:1], doc_example_1[0:1]]
    
    #check that slice of Doc object is indeed a Span
    assert type( term_list[0] )== Span
    assert type( term_list[1] )== Span

    #load an empty TermExtractor ( i.e. without 'any' 'languages' )
    termextractor=TermExtractor( languages=[] )
    
    unique_term_list=termextractor._make_term_list_unique( term_list )
    unique_term_list=[ term.text for term in unique_term_list ]
    
    true_unique_term_list=[ 'Credit' ]
    
    assert true_unique_term_list == unique_term_list
    
def test_term_text_is_clean( ):
    
    '''
    test _term_text_is_clean method of TermExtractor class.
    '''
    
    terms=[ "test",  "test-test", "test term" , "12", "test 12", "test.",  "test , test",  "" ]
    true_flag=[  True, True, True, False, False, False, False, False ] 
    
    #load an empty TermExtractor ( i.e. without 'any' 'languages' )
    termextractor=TermExtractor( languages=[] )
    
    pred_flag=[]
    
    for term in terms:
    
        pred_flag.append( termextractor._term_text_is_clean( term ) )
    
    assert true_flag==pred_flag
    
def test_front_cleaning( doc_example_2 ):
    '''
    test _front_cleaning method of TermExtractor class
    '''
    
    assert type( doc_example_2  ) == Doc

    term_span=doc_example_2[5:]
    
    assert type( term_span )== Span
    
    #check that we took the right span for testing
    assert term_span.text == "the 12 test sentence 23 27"
    
    #load an empty TermExtractor ( i.e. without 'any' 'languages' )
    termextractor=TermExtractor( languages=[] )
    
    #we remove 'the' and '12' from span via _front_cleaning
    cleaned_term_span=termextractor._front_cleaning( term_span )
    
    assert cleaned_term_span.text == "test sentence 23 27"
    
def test_back_cleaning( doc_example_2 ):
    '''
    test _back_cleaning method of TermExtractor class
    '''
    
    assert type( doc_example_2  ) == Doc

    term_span=doc_example_2[5:]
    
    assert type( term_span )== Span
    
    #check that we took the right span for testing
    assert term_span.text == "the 12 test sentence 23 27"
    
    #load an empty TermExtractor ( i.e. without 'any' 'languages' )
    termextractor=TermExtractor( languages=[] )
    
    #we remove '23' and '27' from span via _front_cleaning
    cleaned_term_span=termextractor._back_cleaning( term_span )
    
    assert cleaned_term_span.text == "the 12 test sentence"
    
def test_length_conform(doc_example_2 ):
    
    '''
    test _length_is_conform method of TermExtractor class
    '''
    
    assert type( doc_example_2  ) == Doc

    term_spans=[doc_example_2[:2],doc_example_2[:3] ]

    assert type( term_spans[0] )== Span
    assert type( term_spans[1] )== Span
    
    #check that we took the correct n-gram
    assert term_spans[0].text == 'This is'
    assert term_spans[1].text == 'This is a'

    #load an empty TermExtractor ( i.e. without 'any' 'languages' )
    termextractor=TermExtractor( languages=[], max_ngram=2 )
    
    true_conform=[ True, False ]
    
    pred_conform=[]
    for term_span in term_spans:
        pred_conform.append(termextractor._length_is_conform( term_span )  )
        
    assert true_conform == pred_conform


def test_term_is_not_stopword(doc_example_1 ):
    
    '''
    test _term_is_not_stopword method of TermExtractor class
    '''
    
    assert type( doc_example_1  ) == Doc
    
    term_spans=[doc_example_1[1:2],doc_example_1[:1] ]

    assert type( term_spans[0] )== Span
    assert type( term_spans[1] )== Span
    
    #check that we took the correct n-gram
    assert term_spans[0].text == 'and'  #this one is a stopword
    assert term_spans[1].text == 'Credit' #this one does not contain a stopword

    #load an empty TermExtractor ( i.e. without 'any' 'languages' )
    termextractor=TermExtractor( languages=[ 'en' ], remove_stopwords=True  )
    
    true_stopwords=[ False, True ]
    
    pred_stopwords=[]
    for term_span in term_spans:
        pred_stopwords.append(termextractor._term_is_not_stopword( term_span, 'en' )  )
        
    assert true_stopwords == pred_stopwords
    