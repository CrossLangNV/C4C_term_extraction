import os
import base64
import configparser
from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from cassis.typesystem import load_typesystem

from src.terms.terms import TermExtractor
from src.annotations.annotations import AnnotationAdder
from src.cleaning.cleaning_trafilatura import get_json_trafilatura

MEDIA_ROOT="media"

with open( os.path.join( MEDIA_ROOT, 'typesystem.xml' )  , 'rb') as f:
    TYPESYSTEM = load_typesystem(f)
    
config = configparser.ConfigParser()
config.read( os.path.join( MEDIA_ROOT, 'TermExtraction.config' ))
    
annotation_adder=AnnotationAdder( TYPESYSTEM, config )

#all supported languages: [ 'en', 'de', 'nl', 'fr', 'it', 'nb', 'sl', 'hr']

termextractor=TermExtractor( [ 'en', 'de', 'nl', 'fr', 'it', 'nb', 'sl', 'hr'], max_ngram=10, remove_stopwords=True , use_spellcheck_tool=False )

class Document(BaseModel):
    html: str
    language:Union[str,type(None)]

app=FastAPI()


def create_output_json( document:Document ):
    
    output_json={}
    
    #Extract text from html (i.e. without boilerplate sections such as headers...) using trafilatura library.
    #When document.language!=None, then document.html in other language than document.language will be ignored.
    json_trafilatura=get_json_trafilatura( document.html, target_language=document.language )
    if 'title' in json_trafilatura: #i.e. title tag from html, extracted via BeautifulSoup
        output_json[ 'title' ]=json_trafilatura['title']
    else:
        output_json[ 'title' ]=None
    if 'tags' in json_trafilatura:
        output_json[ 'tags' ]=json_trafilatura['tags']
    else:
        output_json[ 'tags' ]=None
    if 'excerpt' in json_trafilatura:
        output_json[ 'excerpt' ]=json_trafilatura['excerpt']
    else:
        output_json[ 'excerpt']=None
    if 'text' in json_trafilatura:
        output_json[ 'text' ]=json_trafilatura['text']
    else:
        output_json[ 'text' ]=''
    if 'hostname' in json_trafilatura: #e.g. eeklo.be
        output_json[ 'hostname' ]=json_trafilatura['hostname']
    else:
        output_json[ 'hostname' ]=''
    if 'source-hostname' in json_trafilatura: #e.g Stad Eeklo
        output_json[ 'source-hostname' ]=json_trafilatura['source-hostname']
    else:
        output_json[ 'source-hostname' ]=''
    if 'source' in json_trafilatura:  #e.g. https://www.eeklo.be/aangifte-geboorte'
        output_json[ 'source' ]=json_trafilatura['source']
    else:
        output_json[ 'source' ]=''        
    output_json[ 'language' ]=document.language

    return output_json

    
@app.post("/chunking")
async def chunk(document: Document):
    
    output_json=create_output_json( document )
    
    #now add sentence annotations:
    annotation_adder.create_cas_from_text( output_json['text'] )
    annotation_adder.add_sentence_annotation()
    #annotation_adder.add_paragraph_annotation()
    encoded_cas=base64.b64encode(  bytes( annotation_adder.cas.to_xmi()  , 'utf-8' ) ).decode()
    
    output_json[ 'cas_content' ]=encoded_cas
    
    return output_json


@app.post("/extract_terms")
async def term_extraction(document: Document):
    
    if not document.language:
        raise ValueError( "Language should be specified when doing term extraction and named entity recognition." )
    
    output_json=create_output_json( document )

    #now add sentence annotations:
    annotation_adder.create_cas_from_text( output_json['text'] )
    annotation_adder.add_sentence_annotation()
    #annotation_adder.add_paragraph_annotation()
    sentences =  [ sentence.get_covered_text() for \
                  sentence in annotation_adder.cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'SENTENCE_TYPE' ] ) ]
    terms_lemmas, ner_list=termextractor.get_terms_ner( sentences, language=document.language )
    annotation_adder.add_token_annotation( terms_lemmas )
    assert len( ner_list ) == len( sentences ), "For every sentence (annotated via SENTENCE_TYPE) there should be exactly one list of detected named entities provided ( List[Named_entity])"
    annotation_adder.add_named_entity_annotation( ner_list )
    encoded_cas=base64.b64encode(  bytes( annotation_adder.cas.to_xmi()  , 'utf-8' ) ).decode()   
    
    output_json[ 'cas_content' ]=encoded_cas
    
    return output_json