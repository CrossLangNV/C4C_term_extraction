import os
import requests
import base64
import json
import configparser

from cassis.typesystem import load_typesystem
from cassis.xmi import load_cas_from_xmi

MEDIA_ROOT="../media"

with open(os.path.join(MEDIA_ROOT, 'typesystem.xml'), 'rb') as f:
    TYPESYSTEM = load_typesystem(f)
    
config = configparser.ConfigParser()
config.read( os.path.join( MEDIA_ROOT, 'TermExtraction.config' ))

#1) send request with json file for both chunking and term extraction

#This test_text could for example be the result of tika parser.
print( "\n" )
print( "FIRST EXAMPLE" )
print( "\n" )

test_text="This the first test sentence. And this is the second. \n Another sentence \n\n Now we start another paragraph \n\n\n\n \t This is the third paragraph.\n\n"

input_json = {}
input_json['text']=test_text
input_json['language']="en"

r = requests.post(  "http://localhost:5001/extract_terms" , json=input_json )

response_json=json.loads( r.content )

decoded_cas_content=base64.b64decode( response_json['cas_content'] ).decode('utf-8')

cas = load_cas_from_xmi(decoded_cas_content, typesystem=TYPESYSTEM, trusted=True)

print( "Sofa string:\n" )

print(cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).sofa_string )

print( "\n" )

print( "Sentences: \n" )

for sentence in cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'SENTENCE_TYPE' ] ):
    print( sentence.get_covered_text(), "\n" )

print( "Paragraphs: \n" )

for par in cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'PARAGRAPH_TYPE' ] ):
    print( par.get_covered_text(), "\n" )
    
print( "Terms: \n" )

for token in cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'TOKEN_TYPE' ] ):
    print( token.get_covered_text() )
    print( token )
    
print( "Named entities: \n" )

for ner in cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'NER_TYPE' ] ):
    print( ner.get_covered_text() )
    print( ner )

#2) send request with json file only for chunking.
print( "\n" )
print( "SECOND EXAMPLE" )
print( "\n" )

r = requests.post(  "http://localhost:5001/chunking" , json=input_json )

response_json=json.loads( r.content )

decoded_cas_content=base64.b64decode( response_json['cas_content'] ).decode('utf-8')

cas = load_cas_from_xmi(decoded_cas_content, typesystem=TYPESYSTEM, trusted=True)

print( "Sofa string:\n" )

print(cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).sofa_string )

print( "\n" )

print( "Sentences: \n" )

for sentence in cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'SENTENCE_TYPE' ] ):
    print( sentence.get_covered_text(), "\n" )

print( "Paragraphs: \n" )

for par in cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'PARAGRAPH_TYPE' ] ):
    print( par.get_covered_text(), "\n" )


#3) send request with json file with long text (result of tika parsing):
 
text =open( "../user_scripts/example.txt" ).read()

input_json = {}
input_json['text']=text
input_json['language']="nl"

r = requests.post(  "http://localhost:5001/extract_terms" , json=input_json )

response_json=json.loads( r.content )

decoded_cas_content=base64.b64decode( response_json['cas_content'] ).decode('utf-8')

cas = load_cas_from_xmi(decoded_cas_content, typesystem=TYPESYSTEM, trusted=True)

print( "Sofa string:\n" )

print(cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).sofa_string )

print( "\n" )

print( "Sentences: \n" )

for sentence in cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'SENTENCE_TYPE' ] ):
    print( sentence.get_covered_text(), "\n" )

print( "Paragraphs: \n" )

for par in cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'PARAGRAPH_TYPE' ] ):
    print( par.get_covered_text(), "\n" )
    
print( "Terms: \n" )

for token in cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'TOKEN_TYPE' ] ):
    print( token.get_covered_text() )
    print( token )
    
print( "Named entities: \n" )

for ner in cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'NER_TYPE' ] ):
    print( ner.get_covered_text() )
    print( ner )
