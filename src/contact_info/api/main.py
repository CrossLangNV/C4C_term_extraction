from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.contact_info.classification_contact_info import classify_address, classify_contact_type, classify_email, \
    classify_hours, \
    classify_telephone, TypesContactInfo


class Sentence(BaseModel):
    string: str = Field(...,
                        description="A sentence that is expected to contain some contact info.",
                        example='chaussée de Wavre 101a Tel. 0473010203 E-mail: name@mail.com Website: Http://www.nenuphart.be Open Monday, Tuesday')


class SentenceCountry(Sentence):
    country_code: str = Field(...,
                              description="The country code (ISO 3166) to assume for phone numbers.",
                              example="BE"
                              )


class Label(BaseModel):
    name: str


app = FastAPI()


@app.get("/")
async def home():
    """
    Homepage message.

    Returns:

    """
    return {'msg': "Contact information classification API."}


@app.post("/classify_contact_type", response_model=List[Label])
async def post_contact_type(sentence_country: SentenceCountry):
    """
    Predicts the type of contact information.

    Args:
        sentence_country: a sentence with information about country of origin.

    Returns:

    """

    contact_type = classify_contact_type(sentence_country.string,
                                         country_code=sentence_country.country_code)

    return [Label(name=contact_type_i.name) for contact_type_i in contact_type]

    raise HTTPException(status_code=501, detail="Server was unable to detect a type of contact information."
                                                "Please contact a dev for further updates.")


@app.get("/classify_contact_type/labels", response_model=List[str])
async def get_contact_type_labels():
    """
    Retrieve all possible labels that can be given to a contact info sentence.

    Returns:

    """
    return [e.name for e in TypesContactInfo]


@app.post("/classify_contact_type/email", response_model=bool)
async def post_email(sentence: Sentence):
    """
    Individual identifier for contact information for the type 'email'

    Args:
        sentence:

    Returns:

    """
    b_email = classify_email(sentence.string)
    return b_email


@app.post("/classify_contact_type/hours", response_model=bool)
async def post_hours(sentence: Sentence):
    """
    Individual identifier for contact information for the type 'opening hours'

    Args:
        sentence:

    Returns:

    """
    b_hours = classify_hours(sentence.string)
    return b_hours


@app.post("/classify_contact_type/telephone", response_model=bool)
async def post_telephone(sentence_country: SentenceCountry):
    """
    Individual identifier for contact information for the type 'telephone'

    Args:
        sentence:

    Returns:

    """
    b_address = classify_telephone(sentence_country.string,
                                   sentence_country.country_code)
    return b_address


@app.post("/classify_contact_type/address", response_model=bool)
async def post_address(sentence: Sentence):
    """
    Individual identifier for contact information for the type 'address'

    Args:
        sentence:

    Returns:

    """
    b_address = classify_address(sentence.string)
    return b_address
