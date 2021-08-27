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

#test_text="This the first test sentence. And this is the second. \n Another sentence \n\n Now we start another paragraph \n\n\n\n \t This is the third paragraph.\n\n"

test_html='<title>The title </title><p>This the first test sentence.</p><p> And this is the second.</p><p> Another sentence </p><p> Now we start another paragraph </p><p>This is the third paragraph.</p>'

input_json = {}
input_json['html']=test_html
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


#3) send request with json file with long html:
 
test_html =open( "../user_scripts/Aangifte geboorte - Stad Eeklo.html" ).read()

input_json={}
input_json[ 'html' ] = test_html
input_json[  'language' ] = 'nl'

#with open("../user_scripts/Aangifte geboorte - Stad Eeklo.json", 'w') as json_file:
#    json.dump(input_json, json_file)

#input_json=open( "../user_scripts/Aangifte geboorte - Stad Eeklo.json", 'r' ).read()
#input_json=json.loads( input_json )

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
    

#4) a) send request to 'extract_contact_info'
    
test_html =open( "../user_scripts/Aangifte geboorte - Stad Eeklo.html" ).read()

input_json={}
input_json[ 'html' ] = test_html
input_json[  'language' ] = 'nl'

r = requests.post(  "http://localhost:5001/extract_contact_info" , json=input_json )

response_json=json.loads( r.content )

decoded_cas_content=base64.b64decode( response_json['cas_content'] ).decode('utf-8')

cas = load_cas_from_xmi(decoded_cas_content, typesystem=TYPESYSTEM, trusted=True)

for par_contact in cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'CONTACT_PARAGRAPH_TYPE' ] ):
    print( "CONTACT" )
    print( par_contact.content )
    print( "\n" )
    #print( "WITH CONTEXT" )
    #print( par_contact.content_context )
    #print( "\n" )
    
#4) b) send request to 'extract_contact_info'

test_html=open(  "Wat zijn de huidige maatregelen? | Coronavirus COVID-19.html" ).read()

input_json={}
input_json[ 'html' ] = test_html
input_json[  'language' ] = 'nl'

import time
start=time.time()
r = requests.post(  "http://localhost:5001/extract_contact_info" , json=input_json )
end=time.time()
print(  end-start )

response_json=json.loads( r.content )

print( "length", len( response_json['text'].split( "\n" ) ) )

decoded_cas_content=base64.b64decode( response_json['cas_content'] ).decode('utf-8')

cas = load_cas_from_xmi(decoded_cas_content, typesystem=TYPESYSTEM, trusted=True)

for par_contact in cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'CONTACT_PARAGRAPH_TYPE' ] ):
    print( "CONTACT" )
    print( par_contact.content )
    print( "\n" )
    #print( "WITH CONTEXT" )
    #print( par_contact.content_context )
    #print( "\n" )

#4) send request to 'extract_questions_answers'

test_html=open( "Wat zijn de huidige maatregelen? | Coronavirus COVID-19.html" ).read()

input_json={}
input_json[ 'html' ] = test_html
input_json[  'language' ] = 'nl'

import time
start=time.time()
r = requests.post(  "http://localhost:5001/extract_questions_answers" , json=input_json )
end=time.time()
print(  end-start )

response_json=json.loads( r.content )

decoded_cas_content=base64.b64decode( response_json['cas_content'] ).decode('utf-8')

cas = load_cas_from_xmi(decoded_cas_content, typesystem=TYPESYSTEM, trusted=True)

for par_question in cas.get_view( config[ 'Annotation' ][ 'SOFA_ID' ] ).select( config[ 'Annotation' ][ 'QUESTION_PARAGRAPH_TYPE' ] ):
    print( "QUESTION-ANSWER" )
    print( par_question.content_context )
    print( "\n" )
