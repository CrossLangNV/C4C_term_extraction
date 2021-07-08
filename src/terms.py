import string
from typing import List, Dict, Union, Set, Tuple

import spacy
import spacy_udpipe

import de_core_news_lg
import en_core_web_lg
import nl_core_news_lg
import fr_core_news_lg
import nb_core_news_lg
import it_core_news_lg

from nltk.corpus import stopwords as NLTK_STOPWORDS
from spacy.lang.de.stop_words import STOP_WORDS as STOP_WORDS_DE
from spacy.lang.en.stop_words import STOP_WORDS as STOP_WORDS_EN
from spacy.lang.fr.stop_words import STOP_WORDS as STOP_WORDS_FR
from spacy.lang.nl.stop_words import STOP_WORDS as STOP_WORDS_NL
from spacy.lang.it.stop_words import STOP_WORDS as STOP_WORDS_IT
from spacy.lang.sl.stop_words import STOP_WORDS as STOP_WORDS_SL
from spacy.lang.hr.stop_words import STOP_WORDS as STOP_WORDS_HR
from spacy.lang.nb.stop_words import STOP_WORDS as STOP_WORDS_NB

from spacy.lang.de import German
from spacy.lang.en import English
from spacy.lang.nl import Dutch
from spacy.lang.fr import French
from spacy.lang.it import Italian
from spacy.lang.nb import Norwegian
from spacy_udpipe.language import UDPipeLanguage

from spacy.tokens.span import Span
from spacy.tokens.doc import Doc

import language_tool_python
from language_tool_python.server import LanguageTool

class TermExtractor():
    '''
    A TermExtractor. Extracts terms for various languages using a spacy model.
    '''
    
    SUPPORTED_LANGUAGES=[ 'en', 'de', 'nl', 'fr', 'it', 'nb', 'sl', 'hr' ]
    
    INVALID_POS_TAGS = ['DET', 'PUNCT', 'ADP', 'CCONJ', 'SYM', 'NUM', 'PRON', 'SCONJ', 'ADV']
    
    PUNCTUATION_AND_DIGITS = string.punctuation.replace('-', '0123456789').replace('\'', '')  #TO DO: check what happens here

    def __init__( self, languages:List[str], max_ngram:int=10, remove_terms_with_stopwords:bool=False , use_spellcheck_tool:bool=False ):
        '''
        :param languages: List of Strings. Languages to load.
        :param max_ngram: int. Maximum length of the ngram (i.e. max numer of tokens in the ngram).
        :param remove_terms_with_stopwords: bool. Whether to remove (multi-word) terms that contain stopwords.
        :param use_spellcheck_tool: bool. Whether to use the spellcheck tool.
        '''
        
        self._languages=languages
        
        self._nlp_dict=self._load_nlp_models( )
        
        self._remove_terms_with_stopwords=remove_terms_with_stopwords
        
        if self._remove_terms_with_stopwords:
        
            self._stopwords_dict=self._load_stopwords()
        
        self._use_spellcheck_tool=use_spellcheck_tool

        if self._use_spellcheck_tool:
            
            self._spellcheck_dict=self._load_spellcheckers()
        
        self._max_ngram=max_ngram
    
    
    def get_terms( self, sentences: List[str], n_jobs:int=1, batch_size:int=32, language:str='en' )->List[Tuple[ str,str ]]:
        '''
        Function to extract terms from a given set of sentences.
        
        :param sentences: List of strings. Sentences to process.
        :param n_jobs:int. Number of processers to use for Spacy.
        :param batch_size: int. Batch size used by the Spacy model.
        :param language: str. Language of the sentences.
        :return List of Tuples containing the extracted terms and the corresponding lemma.
        '''
        
        if language not in self._languages:
            raise ValueError( f"Language '{language}' not in list of loaded languages {self._languages}. Please initialize TermExtractor object with language '{language}'. Also please make sure language '{language}' is in the list of supported languages {self.SUPPORTED_LANGUAGES}." )
        
        term_list=[]    
        for doc in self._nlp_dict[ language ].pipe( sentences, n_process=n_jobs, batch_size=batch_size ):
            #for each sentence, self._parse_doc returns a list of terms (List of spacy Span objects)
            term_list.extend( self._parse_doc( doc ) )
        
        #remove duplicates from the list of spacy Span objects
        term_list=self._make_term_list_unique( term_list )
        
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
            if not self._length_is_conform( term ):
                continue
            if self._remove_terms_with_stopwords:
                if not self._term_does_not_contain_stopword( term, language ):
                    continue
        
            #append valid terms to the cleaned term list.
            cleaned_term_list.append( term )
        
        #remove duplicates from the list of spacy Span objects. Note we need to remove this a second time because we did front and back cleaning
        #which could have mapped different spacy Span objects to the same spacy Span object.
        cleaned_term_list=self._make_term_list_unique( cleaned_term_list )
        
        #spellcheck the list of terms (Spacy Span objects)
        if self._use_spellcheck_tool:
            cleaned_term_list=self._spellcheck( cleaned_term_list, language )
            
        #get the lemma of each term (terms can be multi-words)
        for i,term in enumerate( cleaned_term_list ):
            lemma=self._lemmatize( term )
            cleaned_term_list[i]=( term.text.strip(), lemma )
          
        return cleaned_term_list


    def _load_nlp_models( self )->Dict[ str, Union[ German, English, Dutch, French, Italian, Norwegian, UDPipeLanguage ] ]:

        print( f"Loading nlp models for the languages { self._languages}..." )
        
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
                    
        print( f"Finished loading nlp models for the languages { self._languages}." )

        return nlp_dict
    
    
    def _load_stopwords( self )->Dict[ str, Set[str] ]:
        
        print( f"Loading stopwords for the languages { self._languages}..." )

        stopwords_dict={}
        for language in self._languages:
            if language not in self.SUPPORTED_LANGUAGES:
                raise ValueError( f"Language '{language}' not supported. Supported languages are {supported_languages}." )
            
            if language=='en':
                stopwords_dict['en'] = STOP_WORDS_EN.union(set(NLTK_STOPWORDS.words('english')))
            elif language=='de':
                stopwords_dict['de'] = STOP_WORDS_DE.union(set(NLTK_STOPWORDS.words('german')))
            elif language=='nl':
                stopwords_dict['nl'] = STOP_WORDS_NL.union(set(NLTK_STOPWORDS.words('dutch')))
            elif language=='fr':
                stopwords_dict['fr'] = STOP_WORDS_FR.union(set(NLTK_STOPWORDS.words('french')))
            elif language=='it':
                stopwords_dict['it'] = STOP_WORDS_IT.union(set(NLTK_STOPWORDS.words('italian')))
            elif language=='sl':
                stopwords_dict['sl'] = STOP_WORDS_SL.union(set(NLTK_STOPWORDS.words('slovene')))
            elif language=='hr':
                stopwords_dict['hr'] = STOP_WORDS_HR
            elif language=='nb':
                stopwords_dict['nb'] = STOP_WORDS_NB
                
        print( f"Finished loading stopwords for the languages { self._languages}." )
        
        return stopwords_dict
    
    
    def _load_spellcheckers( self )->Dict[ str, LanguageTool ]:
        
        print( f"Loading spellcheckers for the languages { self._languages}..." )

        spellcheck_dict={}
        for language in self._languages:
            if language not in self.SUPPORTED_LANGUAGES:
                raise ValueError( f"Language '{language}' not supported. Supported languages are {supported_languages}." )
            
            spellcheck_dict[ language ]=language_tool_python.LanguageTool(language)
                    
        print( f"Finished loading spellcheckers for the languages { self._languages}." )
        
        return spellcheck_dict
    

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
        :return: List of Spacy Span objects.
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

        return terms
    
    
    def _front_cleaning( self, term:Span )->Union[ type(None), Span ]:
        '''
        This function is for cleaning ngrams such as 'of the decision' / 'the decision' / 'as of the decision' to 'decision'
        
        :param term: Span.
        :return: Span.
        '''
        
        location=-1
        for i, token in enumerate(term):
            if token.pos_ in self.INVALID_POS_TAGS:
                if i==(location+1):
                    location=i
        return term[ location+1: ]

    
    def _back_cleaning( self, term:Span )->Union[ type(None), Span ]:
        '''
        This function is for cleaning ngrams such as 'decision with which' / 'decision which' / 'decision as from which' to 'decision'
        
        :param term: Span.
        :return: Span.
        '''
        
        location=len( term )
        for i, token in enumerate( reversed(  term ) ):
            j=len( term )-i-1
            if token.pos_ in self.INVALID_POS_TAGS:
                if j==location-1:
                    location=j
        return term[ :location ]
    
    
    def _term_text_is_clean( self, term_text:str ):
        '''
        Function checks if all characters in the strings are ASCII, if it is not empty string, and if it does not contain any characters in self.PUNCTUATION_AND_DIGITS.
        
        :param term: string. The term to be checked.
        :return: True or False
        '''
        
        if term_text.isascii() and term_text and all(
                not character in self.PUNCTUATION_AND_DIGITS for character in term_text.strip()):
            return True
        else:
            return False
        
        
    def _make_term_list_unique( self, terms: List[Span] )->List[Span]:
        '''
        Function to make list of Span objects unique, based on its self.text value.
        
        :param terms: List[Span].
        :return: List[Span].
        '''
        
        unique_terms=[]
        unique_terms_text=set()
        for term in terms:
            if term.text.strip() not in unique_terms_text:
                unique_terms.append( term )
                unique_terms_text.add( term.text.strip() )

        return unique_terms
    
    def _length_is_conform( self, term:Span )->bool:
        '''
        Check length of the Span object ( the ngram ) (i.e. max numer of tokens in the ngram, should be smaller than self._max_ngram).
        
        :param term: Span.
        :return bool.
        '''
        
        if len( term )<=self._max_ngram:
            return True
        else:
            return False
        

    def _term_does_not_contain_stopword( self, term:Span, language:str )->bool:
        '''
        Check if term does not contain a stopword. If it does contain a stopword, return True, else False. Use loaded stopword list for this.
        
        :param term: Span.
        :param language: String. Language, for stopword list.
        :return bool.
        '''
    
        for item in term:
            if item.text in self._stopwords_dict[ language ]:
                return False
        return True
    
    def _spellcheck( self, terms:List[Span], language:str )-> List[Span]:
        '''
        Spellchecker to clean the list of Spacy Span objects. 
        
        :param terms: List of Span obejcts. 
        :param language: String. Language of the spellchecker.
        :return List of Span objects that passed the spell check.
        '''
        
        spellchecked_terms=[]
        for term in terms:
            m=self._spellcheck_dict[ language ].check( term.text.capitalize() )  #capitalize because spellchecker wants first char of sentence to be uppercase
            #if m ==> spellcheck detected an error in the term
            if not m:
                #means term was correct
                spellchecked_terms.append( term )
        return spellchecked_terms
    
    def _lemmatize( self, term:Span )->str:
        '''
        Lemmatize spacy Span object (lemma will be a string).
        
        :param term:Span. Spacy Span object to lemmatize.
        :return str. Lemmatized multi-word.
        '''
        
        lemma=[]
        for item in term:
            lemma.append( item.lemma_ )
        lemma_term=' '.join( lemma ).strip()
        return lemma_term
    