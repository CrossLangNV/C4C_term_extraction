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
