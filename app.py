import os
import base64
import configparser
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from cassis.typesystem import load_typesystem

from src.terms.terms import TermExtractor
from src.annotations.annotations import AnnotationAdder

MEDIA_ROOT="media"

with open( os.path.join( MEDIA_ROOT, 'typesystem.xml' )  , 'rb') as f:
    TYPESYSTEM = load_typesystem(f)
    
config = configparser.ConfigParser()
config.read( os.path.join( MEDIA_ROOT, 'TermExtraction.config' ))

annotation_adder=AnnotationAdder( TYPESYSTEM, config )

termextractor=TermExtractor( ['en', 'nl' ], max_ngram=10, remove_terms_with_stopwords=False , use_spellcheck_tool=False )

class Document(BaseModel):
    text: str
    language:str

app=FastAPI()

@app.post("/chunking")
async def chunk(document: Document):
    annotation_adder.create_cas_from_text( document.text )
    annotation_adder.add_sentence_annotation()
    annotation_adder.add_paragraph_annotation()
    encoded_cas=base64.b64encode(  bytes( annotation_adder.cas.to_xmi()  , 'utf-8' ) ).decode()   
    
    output_json={}
    output_json[ 'cas_content' ]=encoded_cas
    output_json[ 'language' ]=document.language
    
    return output_json

@app.post("/extract_terms")
async def term_extraction(document: Document):
    annotation_adder.create_cas_from_text( document.text )
    annotation_adder.add_sentence_annotation()
    annotation_adder.add_paragraph_annotation()
    sentences =  [sentence.get_covered_text() for \
                  sentence in annotation_adder.cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'SENTENCE_TYPE' ] )]
    terms_lemmas,_=termextractor.get_terms_ner( sentences, language=document.language )
    annotation_adder.add_token_annotation( terms_lemmas )
    encoded_cas=base64.b64encode(  bytes( annotation_adder.cas.to_xmi()  , 'utf-8' ) ).decode()   
    
    output_json={}
    output_json[ 'cas_content' ]=encoded_cas
    output_json[ 'language' ]=document.language
    
    return output_json