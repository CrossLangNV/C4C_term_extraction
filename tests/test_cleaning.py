import pytest
import os
import json

from src.cleaning.cleaning_trafilatura import get_json_trafilatura

MEDIA_ROOT='tests/test_files'

def test_get_json_trafilatura():
    
    html=open( os.path.join( MEDIA_ROOT, "test.html" ) ).read()
    
    true_json=json.loads( open( os.path.join( MEDIA_ROOT, "json_trafilatura.json" ) ).read() )
        
    json_trafilatura=get_json_trafilatura( html , target_language='en' )
    
    assert true_json == json_trafilatura