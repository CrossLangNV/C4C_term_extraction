from trafilatura import extract
from bs4 import BeautifulSoup
import json

from typing import Dict, Union

def get_json_trafilatura( html:str, target_language=None )->Dict[ str, Union[ type(None), str ] ]:
    
    #title extracted via BeautifulSoup because title extracted via trafilatura is sometimes not complete.
    soup=BeautifulSoup( html, 'html.parser' )
    title=soup.find( 'title' )
    
    #now extract text without boilerplate html:
    json_string=extract( html, include_formatting=False,output_format='json', target_language=target_language )
    if json_string:
        json_trafilatura=json.loads( json_string )
    else:
        json_trafilatura={}
    
    if title:
        json_trafilatura[ 'title' ]=title.text
    return json_trafilatura