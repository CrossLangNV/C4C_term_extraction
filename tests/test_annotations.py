import pytest
from src.annotations.annotations import get_sentences_index, get_paragraphs_index
from src.annotations.utils import is_token

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
