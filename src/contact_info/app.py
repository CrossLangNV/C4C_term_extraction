from fastapi import FastAPI
from pydantic import BaseModel

from .classification_contact_info import classify_contact_type, classify_email


class Sentence(BaseModel):
    string: str


class Label(BaseModel):
    name: str


app = FastAPI()


@app.get("/")
async def home():
    return {'msg': "Contact information classification API."}


@app.post("/classify_contact_type", response_model=Label)
async def post_contact_type(sentence: Sentence):
    contact_type = classify_contact_type(sentence.string)
    return Label(name=contact_type.name)


@app.post("/classify_contact_type/email", response_model=bool)
async def post_email(sentence: Sentence):
    b_email = classify_email(sentence.string)
    return b_email

# TODO other classifiers
