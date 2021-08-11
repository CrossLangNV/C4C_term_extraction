from trafilatura import extract
from bs4 import BeautifulSoup
import json

from typing import Dict, Union

def get_json_trafilatura( html:str, target_language=None )->Dict[ str, Union[ type(None), str ] ]:
    
    '''
    Extract text from html via the trafilatura library. I.e. removal of boilerplate html (headers, footers,..) from html file. If target language is specified, only webpages in the relavant language will be extracted. If set to None, it will be ignored (recommended). The title is extracted using BeautifulSoup.
    
    :param html: string.
    :param target: string or None. None is recommended.
    :return Dict with the following keys (if text extraction via trafilatura was succesfull): 'title', 'author', 'hostname', 'date', 'categories', 'tags', 'fingerprint', 'id', 'license', 'raw-text', 'source', 'source-hostname', 'excerpt', 'text', 'comments'.
    '''
    
    #title extracted via BeautifulSoup because title extracted via trafilatura is sometimes not complete.
    soup=BeautifulSoup( html, 'html.parser' )
    title=soup.find( 'title' )
    
    #now extract text without boilerplate html:
    json_string=extract( html, include_formatting=False, output_format='json', target_language=target_language )
    if json_string:
        json_trafilatura=json.loads( json_string )
    else:
        json_trafilatura={}
    
    if title:
        json_trafilatura[ 'title' ]=title.text
    return json_trafilatura