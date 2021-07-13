from typing import List, Tuple

import ahocorasick as ahc

from configparser import ConfigParser

from cassis.typesystem import TypeSystem
from cassis.cas import Cas

from .utils import is_token

class AnnotationAdder():
    
    '''
    A class for converting text to a Cas object with sentence, paragraph, and token annotations. The latter obtained using a TermExtractor. The cas will be modified inplace and is available via self.cas.
    '''
    
    def __init__( self, typesystem:TypeSystem, config: ConfigParser ):
        
        '''
        :param typesystem: TypeSystem. Typesystem to use.
        :param config: ConfigParser. ConfigParser object with names of annotations.
        '''
        
        self._typesystem=typesystem
        
        #check if config file contains the necessary keys.
        if "Annotation" not in config:
            raise KeyError( "config file should contain 'Annotation' section."  )
            
        if "SOFA_ID" not in config[ "Annotation" ]:
            raise KeyError( "Annotation section of config file should contain 'SOFA_ID'."  )
            
        if "SENTENCE_TYPE" not in config[ "Annotation" ]:
            raise KeyError( "Annotation section of config file should contain 'SENTENCE_TYPE'."  )
            
        if "PARAGRAPH_TYPE" not in config[ "Annotation" ]:
            raise KeyError( "Annotation section of config file should contain 'PARAGRAPH_TYPE'."  )
            
        if "TOKEN_TYPE" not in config[ "Annotation" ]:
            raise KeyError( "Annotation section of config file should contain 'TOKEN_TYPE'." )
                      
        self._config=config
        
        
    def create_cas_from_text( self, text:str ):
        
        '''
        Function to convert text (for example obtained via tika) to a Cas (added as sofa at self._config[ 'Annotation' ][ 'SOFA_ID' ] ). Cas will be available as at self.cas.
        
        :param text: str. Input text.
        '''
                
        self.cas = Cas( typesystem=self._typesystem )
        
        self.cas.create_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).sofa_string=text
        
        
    def add_sentence_annotation( self ):
        
        '''
        Add sentence annotations ( self._config[ 'Annotation' ][ 'SENTENCE_TYPE' ] ) to self.cas using the get_sentences_index() helper function. If self.cas already contains self._config[ 'Annotation' ][ 'SENTENCE_TYPE' ] annotations, the will be removed before adding new ones. 
        '''
        
        #first check if AnnotationAdder contains _cas object:
        if not hasattr( self, 'cas' ):
            raise AttributeError( "AnnotationAdder should contain 'cas' attribute. Please create 'cas' attribute from text via the self.create_cas_from_text method(text), before using the self.add_sentence_annotation() method" )
                
        sentence_type=self._typesystem.get_type( self._config[ 'Annotation' ][ 'SENTENCE_TYPE' ] )

        #check if cas object already contains sentence annotations. If so remove them first
        sentence_annotations=self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ]  ).select( self._config[ 'Annotation' ][ 'SENTENCE_TYPE' ] )
        
        if sentence_annotations:
            print( "self.cas already contains SENTENCE_TYPE annotations. Removing these annotations, before adding new ones." )
            for sentence_annotation in sentence_annotations:
                self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ]  ).remove_annotation( sentence_annotation )
        
        indices_sentences=get_sentences_index( self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).sofa_string )
                
        for index in indices_sentences:

            self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).add_annotation( sentence_type( begin=index[0], end=index[1], id='regular sentence' ) )
            
            
    def add_paragraph_annotation( self ):
        
        '''
        Add paragraph annotations ( self._config[ 'Annotation' ][ 'PARAGRAPH_TYPE' ] ) to self.cas using the get_sentences_index() helper function. If self.cas already contains self._config[ 'Annotation' ][ 'PARAGRAPH_TYPE'] annotations, the will be removed before adding new ones. 
        '''
        
        #first check if AnnotationAdder contains _cas object:
        if not hasattr( self, 'cas' ):
            raise AttributeError( "AnnotationAdder should contain 'cas' attribute. Please create 'cas' attribute from text via the self.create_cas_from_text method(text), before using the self.add_sentence_annotation() method" )
                        
        paragraph_type=self._typesystem.get_type( self._config[ 'Annotation' ][ 'PARAGRAPH_TYPE' ] )

        #check if cas object already contains sentence annotations. If so remove them first
        paragraph_annotations=self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ]  ).select( self._config[ 'Annotation' ][ 'PARAGRAPH_TYPE' ] )
        
        if paragraph_annotations:
            print( "self.cas already contains PARAGRAPH_TYPE annotations. Removing these annotations, before adding new ones." )
            for paragraph_annotation in paragraph_annotations:
                self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ]  ).remove_annotation( paragraph_annotation )
        
        indices_paragraphs=get_paragraphs_index( self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).sofa_string )
                
        for index in indices_paragraphs:

            self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).add_annotation( paragraph_type( begin=index[0], end=index[1] ) )

            
    def add_token_annotation( self, terms_lemmas: List[ Tuple[ str, str ] ] ):
        
        '''
        Add token annotations ( self._config[ 'Annotation' ][ 'TOKEN_TYPE' ] ) to self.cas. Tokens should be provided via the list terms_lemmas ( list of (term, lemma) tuples ).

        :param terms_lemmas: List of (term,lemma) Tuples.
        '''

        #Score given to terms. TODO: change this to tfidf or other score.
        SCORE=1.0
        
        #first check if AnnotationAdder contains _cas object:
        if not hasattr( self, 'cas' ):
            raise AttributeError( "AnnotationAdder should contain 'cas' attribute. Please create 'cas' attribute from text via the self.create_cas_from_text method(text), before using the self.add_sentence_annotation() method" )
            
        token_type=self._typesystem.get_type(  self._config[ 'Annotation' ][ 'TOKEN_TYPE' ] )
            
        #make terms_lemmas list unique (on term.lower() key)
        terms_lemmas_unique=[]
        terms_unique=set()
        for term_lemma in terms_lemmas:
            if term_lemma[0].lower() not in terms_unique:
                terms_lemmas_unique.append( term_lemma )
                terms_unique.add( term_lemma[0].lower() )
        
        #make automaton
        A=ahc.Automaton()
        for term_lemma in terms_lemmas_unique:
            A.add_word( term_lemma[0].lower(), ( SCORE, term_lemma[1].lower(), term_lemma[0].lower()  ) )
        A.make_automaton()
        
        #add token type annotation at correct location using automaton
        for sentence in self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).select( self._config[ 'Annotation' ][ 'SENTENCE_TYPE' ] ):
            text=sentence.get_covered_text().lower()
            for end_index, ( score, lemma, term ) in A.iter( text ):
                if not term:
                    continue
                start_index = end_index - (len(term) - 1)
                #check if detected term in text is not part of other token via is_token
                if is_token( start_index, end_index, text ):
                    self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).add_annotation( \
                     token_type( begin=sentence.begin+start_index, end=sentence.begin+end_index+1, score=SCORE, lemma=lemma, term=term ) )
            
            
def get_sentences_index( text:str )->List[ Tuple[ int, int ] ]:
    
    '''
    Helper function to find offsets of the sentences in a string (sentences are considered strings split via "\n")
    
    :param text: String. String, for instance results of tika parser.
    :return: List[ Tuple[ int, int ] ]. List with offsets of the sentences
    '''
    
    sentences_index=[]
    position=0
    for sentence in text.split( "\n" ):
        if sentence:
            begin_pos=position
            end_pos=position+len( sentence )
            
            #we don't want empty part to be included.
            indent_left=len( sentence) - len( sentence.lstrip() )
            indent_right=len( sentence) - len( sentence.rstrip() )
            
            #we are not interested in index of '  ' or '\t  '
            if sentence.strip():
                sentences_index.append( (begin_pos+indent_left, end_pos-indent_right ) )
            #+1 to account for the "\n" (stripped via .split( "\n" ))
            position+=(len(sentence )+1)
        else:
            #to account for the 'empty' sentences ( i.e. "" )
            position+=1
            
    return sentences_index

def get_paragraphs_index( text:str )->List[ Tuple[ int, int ] ]:
    
    '''
    Helper function to find offsets of the paragraphs in a string ( consecutive sentences (obtained via text.split("\n") ) for which sentence.strip() is not None are considered paragraphs.
    
    :param text: String. String, for instance results of tika parser.
    :return: List[ Tuple[ int, int ] ]. List with offsets of the paragraphs.
    '''
    
    in_paragraph=False
    paragraphs_index=[]
    position=0
    sentences=text.split( "\n" )
    for i, sentence in enumerate( sentences  ):
        
        if sentence.strip():
            if in_paragraph==False:
                #this means a new start
                #start_index=i
                start_position=position
            in_paragraph=True
            position+=( len(sentence)+1 ) #+1 to account for the "\n" (stripped via .split( "\n" ))
        else:
            #this means the paragraph has come to and end ( i.e. sentence only contains tabs, spaces... ):
            if in_paragraph==True:
                #end_index=i
                paragraphs_index.append( ( start_position, position-1 ) )  #-1 because the "\n" should not be included in the paragraph
            in_paragraph=False
            position+=(len( sentence )+1) #+1 to account for the "\n" (stripped via .split( "\n" ))
        
        #still works if text ends with two or three sentences? TO DO check
        if i==len( sentences )-1 and in_paragraph:
            paragraphs_index.append( ( start_position, position-1 ) )
            
    return paragraphs_index