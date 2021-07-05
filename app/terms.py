import string
from typing import List, Dict, Union

import spacy
import spacy_udpipe

import de_core_news_lg
import en_core_web_lg
import nl_core_news_lg
import fr_core_news_lg
import nb_core_news_lg
import it_core_news_lg

from spacy.lang.de import German
from spacy.lang.en import English
from spacy.lang.nl import Dutch
from spacy.lang.fr import French
from spacy.lang.it import Italian
from spacy.lang.nb import Norwegian
from spacy_udpipe.language import UDPipeLanguage

from spacy.tokens.span import Span
from spacy.tokens.doc import Doc

class TermExtractor():
    '''
    A TermExtractor.
    '''
    
    SUPPORTED_LANGUAGES=[ 'en', 'de', 'nl', 'fr', 'it', 'nb', 'sl', 'hr' ]
    
    INVALID_POS_TAGS = ['DET', 'PUNCT', 'ADP', 'CCONJ', 'SYM', 'NUM', 'PRON', 'SCONJ', 'ADV']
    
    PUNCTUATION_AND_DIGITS = string.punctuation.replace('-', '0123456789').replace('\'', '')  #TO DO: check what happens here

    def __init__( self, languages:List[str] ):
        
        '''
        :param languages: Languages to load.
        '''
        
        self._languages=languages
            
        self._nlp_dict=self._load_nlp_models( )
        
    
    def get_terms( self, sentences: List[str], n_jobs:int=1, batch_size:int=32, language:str='en' ):
        
        term_list=[]    
        for doc in self._nlp_dict[ language ].pipe( sentences, n_process=n_jobs, batch_size=batch_size ):
            #for each sentence we return a list of terms (List of spacy Token objects)
            term_list.extend( self._parse_doc( doc ) )
        
        cleaned_term_list=[]
        for term in term_list:
            #if not clean, continue
            if not self._term_text_is_clean( term.text ):
                continue
            term=self._front_cleaning( term )
            if not term:
                continue
            term=self._back_cleaning( term )
            if not term:
                continue
            cleaned_term_list.append( term )
                
        #TO DO: should make this list of terms unique.
                
        return cleaned_term_list

    
    def _load_nlp_models( self )->Dict[ str, Union[ German, English, Dutch, French, Italian, Norwegian, UDPipeLanguage ] ]:

        nlp_dict={}
        for language in self._languages:
            if language not in self.SUPPORTED_LANGUAGES:
                raise ValueError( f"Language '{language}' not supported. Supported languages are {supported_languages}." )

            if language=='en': 
                nlp_dict[ language ]=en_core_web_lg.load()
            elif language=='de':
                nlp_dict[ language ]=de_core_news_lg.load()
            elif language=='nl':
                nlp_dict[ language ]=nl_core_news_lg.load()
            elif language=='fr':
                nlp_dict[ language ]=fr_core_news_lg.load()
            elif language=='it':
                nlp_dict[ language ]=it_core_news_lg.load()
            elif language=='nb':
                nlp_dict[ language ]=nb_core_news_lg.load()
            elif language=='sl':
                try:
                    #this throws generic Exception when 'sl' model is not downloaded first
                    nlp_dict[ 'sl' ] = spacy_udpipe.load("sl")
                except:
                    spacy_udpipe.download( 'sl' )
                    nlp_dict[ 'sl' ] = spacy_udpipe.load( 'sl' )
            elif language=='hr':    
                try:
                    #this throws generic Exception when 'hr' model is not downloaded first
                    nlp_dict[ 'hr' ] = spacy_udpipe.load( 'hr' )
                except:
                    spacy_udpipe.download( 'hr' )
                    nlp_dict[ 'hr' ] = spacy_udpipe.load( 'hr' )

        return nlp_dict
    
    def _parse_doc( self, doc:Doc )->List[Span]:
        '''
        Here we rely on the dependency parser, each noun or pronoun is the root of a noun phrase tree, e.g.:
        "I've just watched 'Eternal Sunshine of the Spotless Mind' and found it corny"

        We iterate over each branch of the tree and yield the Doc spans that contain:
            1. the root : 'sunshine'
            2. left branch + the root : 'eternal sunshine'
            3. the root + right branch : 'sunshine of the spotless mind'
            4. left branch + the root + right branch : 'eternal sunshine of the spotless mind'

        :param doc: SpaCy Doc object
        :return: yields various noun phrases
        '''

        terms=[]

        for token in doc:
            if token.pos_ == 'NOUN' or token.pos_ == 'PROPN':
                #this is the NOUN/PROPN:
                terms.append( doc[token.i:token.i+1 ] )
                #this is the right edge:
                terms.append( doc[token.i:token.right_edge.i + 1] )
                #this is right and left edge:
                terms.append( doc[token.left_edge.i:token.right_edge.i + 1] )
                #this is left edge:
                terms.append( doc[token.left_edge.i: token.i + 1] )

        return list(set( terms ))
    
    
    def _front_cleaning( self, term:Span )->Union[ type(None), Span ]:
        
        location=-1
        for i, token in enumerate(term):
            if token.pos_ in self.INVALID_POS_TAGS:
                if i==(location+1):
                    location=i
        return term[ location+1: ]

    def _back_cleaning( self, term:Span )->Union[ type(None), Span ]:
        
        location=len( term )
        for i, token in enumerate( reversed(  term ) ):
            j=len( term )-i-1
            if token.pos_ in self.INVALID_POS_TAGS:
                if j==location-1:
                    location=j
        return term[ :location ]
    
    def _term_text_is_clean( self, term_text:str ):
        """

        :param term: string. The term to be checked.
        :return: True or False
        """
        if term_text.isascii() and all(
                not character in self.PUNCTUATION_AND_DIGITS for character in term_text.strip()):
            return True
        else:
            return False
        
    