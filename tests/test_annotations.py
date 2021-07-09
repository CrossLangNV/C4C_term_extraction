import pytest
from src.annotations import get_sentences_index, get_paragraphs_index

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