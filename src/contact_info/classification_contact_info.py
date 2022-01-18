"""
methods/API/... to classify the contact information further into address, telephone number, email, opening hours...
"""

import re
from enum import auto, Enum
from typing import List

import nltk
import phonenumbers
from nltk.tokenize import word_tokenize
from postal.parser import parse_address


class TypesContactInfo(Enum):
    """
    Using auto, because we don't need a value.

    TODO
        should this be changed to string values?
    """
    EMAIL = auto()
    PHONE = auto()
    HOURS = auto()
    ADDRESS = auto()


def classify_contact_type(s: str,
                          country_code: str) -> List[TypesContactInfo]:
    """

    Returns:

    """

    l_type = []

    if classify_email(s):
        l_type.append(TypesContactInfo.EMAIL)

    if classify_address(s):
        l_type.append(TypesContactInfo.ADDRESS)

    if classify_hours(s):
        l_type.append(TypesContactInfo.HOURS)

    if classify_telephone(s, country_code=country_code):
        l_type.append(TypesContactInfo.PHONE)

    return l_type


def classify_email(s: str,
                   validate: bool = False) -> bool:
    """
    If an email pattern is recognized in the string, it classified as email information

    Args:
        s (str): sentence to be classified
        validate (bool): flag to do an extra check if the email is valid as well.

    Returns:

    TODO
        Decide if it makes sense to validate the email, for extra security: avoiding false positives.
    """

    pattern_at_sign = r"[\w\.-]+@[\w\.-]+"

    matches = re.findall(pattern_at_sign, s)

    if validate:
        pattern_valid_email = r"/^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/"

        for match in matches:
            re.fullmatch(pattern_valid_email, match)

    return bool(matches)


def classify_hours(s: str) -> bool:
    """
    Classify whether a string contains opening hours info or not.

    Args:
        s: sentence with contact info that possibly contains openings hours info.

    Returns:
        boolean: True if the sentence contained opening hours' info; False if not.

    """

    text_tokenized = word_tokenize(s)
    text_tokenized_lower = list(map(str.lower, text_tokenized))

    """
    Days of the week
    """
    allow_list = [
        "Monday", "Mon", "Mo",
        "Tuesday", "Tue", "Tu",
        "Wednesday", "Wed", "We",  # TODO 'We' could lead to lots of false positives.
        "Thursday", "Thu", "Th",
        "Friday", "Fri", "Fr",
        "Saturday", "Sat", "Sa",
        "Sunday", "Sun", "Su"
    ]
    allow_list_lower = list(map(str.lower, allow_list))

    # Find
    for allow in allow_list_lower:
        if allow in text_tokenized_lower:
            return True

    """
    Detect a time.
    
    within word boundaries
    then HH:MM or HH'h'MM
    """
    pattern_time = r"\b([0-1][0-9]|[2][0-3]|[0-9])[h:]([0-5][0-9])\b"

    matches = re.findall(pattern_time, s)

    if bool(matches):
        return bool(matches)

    return False


def classify_address(text: str,
                     ) -> bool:
    """
    classifier to check if a sentence contains an address or not.

    Is currently based on https://stackoverflow.com/a/38506078/6921921

    Args:
        s:

    Returns:

    """

    class Address():
        CITY = "city"
        ROAD = "road"
        HOUSE_NUMBER = "house_number"

        def __init__(self, text):
            self.text = text

            address_parsed = parse_address(text,
                                           language=None, country=None  # TODO use extra info
                                           )

            self.cities = []
            self.roads = []
            self.house_numbers = []

            for s, label in address_parsed:
                if label == self.CITY:
                    self.cities.append(s)
                elif label == self.ROAD:
                    self.roads.append(s)
                elif label == self.HOUSE_NUMBER:
                    self.house_numbers.append(s)

        def classify(self):
            """
            If it has a city or street information, it will return true

            Returns:

            """

            if 0:
                # While it looks nice, it doesn't work consistently
                for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(text))):

                    if hasattr(chunk, "label"):
                        if chunk.label() == "GPE" or chunk.label() == "GSP":
                            return True

                return False

            else:
                return bool(self.cities) or bool(self.roads)

    address = Address(text)

    return address.classify()


def classify_telephone(s: str,
                       country_code: str,
                       debug=False) -> bool:
    """

    Args:
        s:
        country_code: # TODO probably needed
        validate:

    Returns:

    """

    """
    Find numbers and sequence of numbers. 
    ' ', '/', '.', '(', ')', '+' are all allowed.
    """

    ### OLD

    if True:
        # This is a possibility if we know the country of origin. Else it will be too coarsly.

        possible_telephone_numbers = []
        for match in list(phonenumbers.PhoneNumberMatcher(s,
                                                          country_code,
                                                          leniency=phonenumbers.Leniency.POSSIBLE)
                          ):
            if debug:
                print(match)
            possible_telephone_numbers.append(match.number)

    else:
        pattern_telephone = r"\d+(?:[\s.\/]+\d+){0,}"
        possible_telephone_numbers = re.findall(pattern_telephone, s)

        # phonenumbers.is_valid_number(possible_telephone_number)
        possible_telephone_numbers = list(
            filter(lambda s: phonenumbers.is_possible_number(phonenumbers.parse(s, country_code)),
                   possible_telephone_numbers))

    return bool(len(possible_telephone_numbers))
