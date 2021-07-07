#https://github.com/explosion/spaCy/blob/f22704621ef5d136e00a47068288bf55f666716d/spacy/tests/conftest.py#L70
#https://stackoverflow.com/questions/56728218/how-to-mock-spacy-models-doc-objects-for-unit-tests

import pytest


# Arrange
@pytest.fixture()
def first_entry():
    return "a"


# Arrange
@pytest.fixture()
def order(first_entry):
    return [first_entry]


def test_string(order):
    # Act
    order.append("b")

    # Assert
    assert order == ["a", "b"]


def test_int(order):
    # Act
    order.append(2)

    # Assert
    assert order == ["a", 2]



def testing():
    assert 0==0