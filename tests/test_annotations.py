import os

import configparser

from cassis.typesystem import load_typesystem

import pytest
from src.annotations.annotations import AnnotationAdder, get_sentences_index, get_paragraphs_index
from src.annotations.utils import is_token

MEDIA_ROOT='tests/test_files'
                        
with open( os.path.join( MEDIA_ROOT, 'typesystem.xml' )  , 'rb') as f:
    TYPESYSTEM = load_typesystem(f)

config = configparser.ConfigParser()
config.read( os.path.join( MEDIA_ROOT, 'TermExtraction.config' ))

@pytest.fixture()
def annotation_adder():
    return AnnotationAdder( TYPESYSTEM, config)

#fixture makes sure each test that uses annotation_adder gets it own fresh object AnnotationAdder object.
@pytest.mark.parametrize(
    "text,this_annotation_adder",
    [
     ("This is a sentence\n Another one\n\n other\n\n","annotation_adder" ),
     ("","annotation_adder" ),
     ("\n","annotation_adder" ),
    ]
)
def test_create_cas_from_text( text, this_annotation_adder, request ):
    
    annotation_adder=request.getfixturevalue( this_annotation_adder )
    annotation_adder.create_cas_from_text( text )
    assert annotation_adder.cas.get_view( config[ 'Annotation' ]['SOFA_ID'] ).sofa_string == text

    
@pytest.mark.parametrize(
    "text,sentences, offsets,this_annotation_adder",
    [
     ("This is a sentence\n Another one\n\n other\n\n",
      ['This is a sentence', 'Another one', 'other'],
      [(0, 18), (20, 31), (34, 39)],
      "annotation_adder" ),
     ("",
      [],
      [],
      "annotation_adder" ),
     ("\n",
      [],
      [],
      "annotation_adder" ),
     ("t\n",
      ['t'],
      [(0,1)],
      "annotation_adder" ),
    ]
)
def test_add_sentence_annotation( text, sentences, offsets, this_annotation_adder, request ):
    
    annotation_adder=request.getfixturevalue( this_annotation_adder )
    annotation_adder.create_cas_from_text( text )
    assert annotation_adder.cas.get_view( config[ 'Annotation' ]['SOFA_ID'] ).sofa_string == text
    annotation_adder.add_sentence_annotation()
    sentences_pred=annotation_adder.cas.get_view( config[ 'Annotation' ]['SOFA_ID']  ).select( config[ 'Annotation' ]['SENTENCE_TYPE'] )
    sentences_pred_text=[ sentence.get_covered_text() for sentence in sentences_pred ]
    offsets_pred=[ (sentence.begin, sentence.end ) for sentence in sentences_pred ]
    assert sentences_pred_text == sentences
    assert offsets_pred == offsets
    
    
@pytest.mark.parametrize(
    "text,paragraphs, offsets,this_annotation_adder",
    [
     ("  This is a sentence\n Another one\n\n other\n\n",
      ['  This is a sentence\n Another one', ' other'],
      [(0, 33), (35, 41)] ,
      "annotation_adder" ),
     ("",
      [],
      [],
      "annotation_adder" ),
     ("\n",
      [],
      [],
      "annotation_adder" ),
     ("\t   t\n",
      ['\t   t'],
      [(0,5)],
      "annotation_adder" ),
    ]
)
def test_add_paragraph_annotation( text, paragraphs, offsets, this_annotation_adder, request ):
    
    annotation_adder=request.getfixturevalue( this_annotation_adder )
    annotation_adder.create_cas_from_text( text )
    assert annotation_adder.cas.get_view( config[ 'Annotation' ]['SOFA_ID'] ).sofa_string == text
    annotation_adder.add_paragraph_annotation()
    par_pred=annotation_adder.cas.get_view( config[ 'Annotation' ]['SOFA_ID']  ).select( config[ 'Annotation' ]['PARAGRAPH_TYPE'] )
    par_pred_text=[ par.get_covered_text() for par in par_pred ]
    offsets_pred=[ (par.begin, par.end ) for par in par_pred ]
    assert par_pred_text == paragraphs
    assert offsets_pred == offsets
    
    
@pytest.mark.parametrize(
    "text, tokens, offsets,this_annotation_adder",
    [
     ("  This is a sentence\n Another one\n\n other\n\n",
      ['This', 'a sentence', 'other'],
      [(2, 6), (10, 20), (36, 41)] ,
      "annotation_adder" ),
     ("",
      [],
      [],
      "annotation_adder" ),
     ("\n",
      [],
      [],
      "annotation_adder" ),
     ("\t   t\n",
      ['t'],
      [(4,5)],
      "annotation_adder" ),
    ]
)
def test_add_token_annotation( text, tokens, offsets, this_annotation_adder, request ):
    
    #the so called detected terms and lemmas ==> this should typically be obtained via a TermExtractor.
    terms_lemmas=[ ('this', 'this' ), ('a sentence', 'a sentence'  ), ('other', 'other' ), ( 'the', 'the' ), ( 't', 't' ) ]
    
    annotation_adder=request.getfixturevalue( this_annotation_adder )
    annotation_adder.create_cas_from_text( text )
    assert annotation_adder.cas.get_view( config[ 'Annotation' ]['SOFA_ID'] ).sofa_string == text
    #need to add sentence annotations before we can add token annotations.
    annotation_adder.add_token_annotation( terms_lemmas )
    token_pred=annotation_adder.cas.get_view( config[ 'Annotation' ]['SOFA_ID']  ).select( config[ 'Annotation' ]['TOKEN_TYPE'] )
    token_pred_text=[ token.get_covered_text() for token in token_pred ]
    offsets_pred=[ (token.begin, token.end ) for token in token_pred ]
    assert token_pred_text == tokens
    assert offsets_pred == offsets
    
    
@pytest.mark.parametrize(
    "text,sentence_indices",
    [
    ( "  this is a test  \n\n\n\n  \n test sentence \n test sentence \n \t \n tes\n test \ntest\ntest",
    [(2, 16), (26, 39), (42, 55), (62, 65), (67, 71), (73, 77), (78, 82)] ),
    ( "  this is a test  \n\n\n\n  \n test sentence \n tes\n test \ntest\n\n  ",
    [(2, 16), (26, 39), (42, 45), (47, 51), (53, 57)] ),
    ( "\n \t \n  this is a test  \n\n\n\n  \n test sentence \n tes\n test \ntest\n\n  ",
    [(7, 21), (31, 44), (47, 50), (52, 56), (58, 62)] ),
    ( "",
    [] ),
    ( "    ",
    [] ),
    ( "\t",
    [] ),   
    ( "\n",
    [] ),
    ( "\ntest\n",
    [(1, 5)] ),
    ( "\n test\n",
    [(2, 6)] ),
    ],
)
def test_get_sentences_index( text, sentence_indices ):
    '''
    Unit test for get_sentences_index function.
    '''
    
    assert sentence_indices == get_sentences_index( text )


@pytest.mark.parametrize(
    "text,paragraph_indices",
    [
    ( "  this is a test  \n\n\n\n  \n test sentence \n test sentence \n \t \n tes\n test \ntest\ntest",
    [(0, 18), (25, 56), (61, 82)] ),
    ( "  this is a test  \n\n\n\n  \n test sentence \n tes\n test \ntest\n\n  ",
    [(0, 18), (25, 57)] ),
    ( "\n \t \n  this is a test  \n\n\n\n  \n test sentence \n tes\n test \ntest\n\n  ",
    [(5, 23), (30, 62)] ),
    ( "",
    [] ),
    ( "    ",
    [] ),
    ( "\t",
    [] ),   
    ( "\n",
    [] ),
    ( "\ntest\n",
    [(1, 5)] ),
    ( "\n test\n",
    [(1, 6)] ),
    ],
)
def test_get_sentences_index( text, paragraph_indices ):
    '''
    Unit test for get_paragraphs_index.
    '''
    assert paragraph_indices == get_paragraphs_index( text )
    
    
@pytest.mark.parametrize(
    "text,start_end_index,true_result",
    [
    ("test term text",
    (5,8),
    True),
    ("test termtext",
    (5,8),
    False),
    ("test termtext",
    (5,12),
    True),
    ("test-termtext",
    (5,12),
    False),
    ("test-termtext",
    (5,12),
    False),
    ("term termtex",
    (0,3),
    True),
    ("term-termtext",
    (0,3),
    False),
    ("term-termtext",
    (0,0),
    False),
    ("term-termtext",
    (0,12),
    True),
    ("f g",
    (2,2),
    True),
    ("fg",
    (1,1),
    False),
    ],
) 
def test_is_token( text, start_end_index, true_result ):
    
    '''
    Unit test for is_token.
    '''
    
    assert true_result==is_token( start_end_index[0], start_end_index[1], text, special_characters=[ "-","_","+"] )
    

@pytest.mark.parametrize(
    "text,start_end_index,true_result",
    [
    ("test-termtext",
    (5,12),
    True),
    ("term-termtext",
    (0,3),
    True),
    ],
) 
def test_is_token_special_characters( text, start_end_index, true_result ):
    
    '''
    Unit test for is_token (with focus on special characters). 
    '''
    
    assert true_result==is_token( start_end_index[0], start_end_index[1], text, special_characters=["_","+"] )
