from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.contact_info.classification_contact_info import classify_contact_type, classify_email, classify_hours, \
    TypesContactInfo


class Sentence(BaseModel):
    string: str


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


@app.post("/classify_contact_type", response_model=Label)
async def post_contact_type(sentence: Sentence):
    """
    Predicts the type of contact information.

    Args:
        sentence:

    Returns:

    """
    contact_type = classify_contact_type(sentence.string)
    if contact_type:
        return Label(name=contact_type.name)
    else:
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

# TODO other classifiers
