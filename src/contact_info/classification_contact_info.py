"""
methods/API/... to classify the contact information further into address, telephone number, email, opening hours...

TODO
 - Implement 4 classifiers,
 - Implement combined classifier
 - Have an API.
 - Write connector for this API
 - connect to CPSV-AP pipeline, see other repo
 - Check the data that classifies contact info, perhaps we can use something from that.
 - Write REGEX code for some of the classifiers, e.g.
    - telephone numbers: 'numbers, spaces, dots, slashes'
    - opening hours is all about hours and days.
    - Address (?), street + number + city?
"""

import re
from enum import Enum, auto
from typing import Union
from nltk.tokenize import word_tokenize


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


def classify_contact_type(s: str) -> Union[None, TypesContactInfo]:
    """

    Returns:

    """

    if classify_email(s):
        return TypesContactInfo.EMAIL

    # TODO for rest

    return None


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
