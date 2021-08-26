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
from src.cleaning.cleaning_tika import get_text_tika

from src.sentence_classification.trainer_bert_sequence_classifier import TrainerBertSequenceClassifier

#path to the model for sentence classification:
PATH_MODEL="/work/models"
#path to the media folder ( typesystem and config file with names of the annotations )
MEDIA_ROOT="media"

#load the model for sentence classification
trainer_bert_sequence_classifier=\
    TrainerBertSequenceClassifier( \
    pretrained_model_name_or_path= PATH_MODEL, model_type='DISTILBERT' )

with open( os.path.join( MEDIA_ROOT, 'typesystem.xml' )  , 'rb') as f:
    TYPESYSTEM = load_typesystem(f)
    
#Load config file with the annotations
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
    sentences =  [ sentence.get_covered_text() for \
                  sentence in annotation_adder.cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'SENTENCE_TYPE' ] ) ]
    terms_lemmas, ner_list=termextractor.get_terms_ner( sentences, language=document.language )
    annotation_adder.add_token_annotation( terms_lemmas )
    assert len( ner_list ) == len( sentences ), "For every sentence (annotated via SENTENCE_TYPE) there should be exactly one list of detected named entities provided ( List[Named_entity])"
    annotation_adder.add_named_entity_annotation( ner_list )
    encoded_cas=base64.b64encode(  bytes( annotation_adder.cas.to_xmi()  , 'utf-8' ) ).decode()   
    
    output_json[ 'cas_content' ]=encoded_cas
    
    return output_json


@app.post("/extract_contact_info")
async def contact_info_extraction(document: Document):
    
    output_json={}
    
    #parse html input with tika:
    text=get_text_tika( document.html )
    output_json[ 'text' ]=text
    
    annotation_adder.create_cas_from_text( output_json['text'] )
    #add paragraphs to be send to sentence classifier for contact info classification ( DISTILBERT sequence classifier )
    annotation_adder.add_paragraph_annotation( parsing_method='tika' )
    #add sentences
    annotation_adder.add_sentence_annotation()
    
    paragraphs=[]
    paragraphs=list( annotation_adder.cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'PARAGRAPH_TYPE' ] ) )
    
    paragraphs_text=[]
    for par in paragraphs:
        paragraphs_text.append( par.get_covered_text().replace(  "\n", " " ).replace( "\t", " "  ).strip() )
    
    #sanity check
    assert len( paragraphs ) == len( paragraphs_text )
    
    pred_labels, _ = trainer_bert_sequence_classifier.predict( paragraphs_text  )
    
    #sanity check
    assert len( pred_labels ) == len( paragraphs_text )

    for label, par in zip( pred_labels, paragraphs ):
        if label == 1:
            par.divType='contact'
            par.content=par.get_covered_text().strip()
    
    #merge consecutive PARAGRAPH_TYPE annotations into the 'CONTACT_PARAGRAPH_TYPE' annotation,
    annotation_adder.add_contact_annotation( label='contact' )
    #add context (i.e. preceding and appending SENTENCE_TYPE annotations) to content_context attribute of the 'CONTACT_PARAGRAPH_TYPE' features.
    annotation_adder.add_context( root_type='CONTACT_PARAGRAPH_TYPE' , type_to_add='SENTENCE_TYPE' )  
    
    encoded_cas=base64.b64encode(  bytes( annotation_adder.cas.to_xmi()  , 'utf-8' ) ).decode()   
    output_json[ 'cas_content' ]=encoded_cas
    output_json[ 'language' ]=document.language
    
    return output_json