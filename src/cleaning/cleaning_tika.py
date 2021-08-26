import tempfile

from pathlib import Path
import tika

tika.initVM()

from tika import parser

def get_text_tika( html:str )->str:

    '''
    Extract text from html file using tika parser.
    
    :param html: Input html.
    :return String. Parsed text.
    '''

    tmp_name="temp.txt"
    with tempfile.NamedTemporaryFile( mode='w+t' ) as temp:
        temp.write( html )
        text=tikaToText(  temp.name )
    
    if text==None:
        print( "Could not extract text from input html" )
        text=''
    return text

def tikaToText(path_file ):
    parsed = parser.from_file(path_file)
    content = parsed["content"]
    if content:
        return content.strip()