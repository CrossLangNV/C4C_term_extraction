import requests
import sys
from datetime import datetime

import json

from bs4 import BeautifulSoup

#PATH_TO_LINKS="/notebook/nas-trainings/arne/C4C_concepts_extraction/C4C_concepts_extraction/DATA/BECI/not_use_scrapy.txt"
#OUTPUT_FILE="/notebook/nas-trainings/arne/C4C_concepts_extraction/C4C_concepts_extraction/DATA/BECI/output_not_use_scrapy.jsonl"

PATH_TO_LINKS="/notebook/nas-trainings/arne/C4C_concepts_extraction/C4C_concepts_extraction/DATA/BECI/use_scrapy.txt"
OUTPUT_FILE="/notebook/nas-trainings/arne/C4C_concepts_extraction/C4C_concepts_extraction/DATA/BECI/output_use_scrapy.jsonl"

links=open(  PATH_TO_LINKS ).read().strip( "\n" ).split( "\n" )

with open( OUTPUT_FILE , 'w' ) as outfile:

    for i,url in enumerate( links ):

        print( "processing link:", i )

        r = requests.get(url, allow_redirects=True, verify=False )
        #open('brugge_aangifte_geboorte', 'wb').write(r.content)
        html=r.text
        
        soup3=BeautifulSoup( html  ,'html.parser')

        #Get all title tags
        title_tags=soup3.findAll( 'title' )
        if title_tags:
            titles="\n".join([  title.text for title in title_tags  ])

        dict_file={}
        dict_file[ 'url' ]=url
        dict_file[ 'title' ]=titles
        dict_file[ 'website' ]=''
        dict_file[ 'content_html' ]=html
        dict_file[ 'date' ]=str(datetime.now())

        json.dump( dict_file, outfile )
        outfile.write( "\n" ) 