from typing import List, Tuple

import ahocorasick as ahc

from configparser import ConfigParser

from cassis.typesystem import TypeSystem
from cassis.cas import Cas

from .utils import is_token
from ..aliases import Named_entity, Term_lemma

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
            
        if "NER_TYPE" not in config[ "Annotation" ]:
            raise KeyError( "Annotation section of config file should contain 'NER_TYPE'." )
                                 
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
            
            
    def add_paragraph_annotation( self, parsing_method:str='tika' ):
        
        '''
        Add paragraph annotations ( self._config[ 'Annotation' ][ 'PARAGRAPH_TYPE' ] ) to self.cas using the get_paragraphs_index() or get_paragraphs_index_trafilatura() helper functions dending on what method was used to obtain the text in self._config[ 'Annotation' ][ 'SOFA_ID' ]  ). If self.cas already contains self._config[ 'Annotation' ][ 'PARAGRAPH_TYPE'] annotations, the will be removed before adding new ones. 
        
        :param parsing_method: string. Parsing method. Should be either 'tika' or 'trafilatura'.
        '''
        
        #first check if AnnotationAdder contains _cas object:
        if not hasattr( self, 'cas' ):
            raise AttributeError( "AnnotationAdder should contain 'cas' attribute. Please create 'cas' attribute from text via the self.create_cas_from_text method(text), before using the self.add_sentence_annotation() method" )
            
        if parsing_method not in [ 'tika', 'trafilatura' ]:
            raise ValueError( f"parsing method should be either 'tika' or 'trafilatura', but received { parsing_method}." )
                        
        paragraph_type=self._typesystem.get_type( self._config[ 'Annotation' ][ 'PARAGRAPH_TYPE' ] )

        #check if cas object already contains paragraph annotations. If so remove them first
        paragraph_annotations=self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ]  ).select( self._config[ 'Annotation' ][ 'PARAGRAPH_TYPE' ] )
        
        if paragraph_annotations:
            print( "self.cas already contains PARAGRAPH_TYPE annotations. Removing these annotations, before adding new ones." )
            for paragraph_annotation in paragraph_annotations:
                self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ]  ).remove_annotation( paragraph_annotation )
        
        if parsing_method=='tika':
            indices_paragraphs=get_paragraphs_index( self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).sofa_string )
        elif parsing_method=='trafilatura':
            indices_paragraphs=get_paragraphs_index_trafilatura( self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).sofa_string )
                
        for index in indices_paragraphs:

            self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).add_annotation( paragraph_type( begin=index[0], end=index[1] ) )

            
    def add_token_annotation( self, terms_lemmas: List[ Term_lemma ] ):
        
        '''
        Add token annotations ( self._config[ 'Annotation' ][ 'TOKEN_TYPE' ] ) to self.cas. Tokens should be provided via the list terms_lemmas ( list of (term, lemma) tuples ).

        :param terms_lemmas: List of (term,lemma) Tuples.
        '''
        
        #Score given to terms. TODO: change this to tfidf or other score.
        SCORE=1.0
        
        if not terms_lemmas:
            print( "List of terms and lemmas is empty. Not adding any TOKEN_TYPE annotations to the cas." )
            return
        
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
        
        sentences=self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).select( self._config[ 'Annotation' ][ 'SENTENCE_TYPE' ] )
        if not sentences:
            print( "self.cas does not contain sentences ( SENTENCE_TYPE ). Adding sentence annotations via the .add_sentence_annotation() method." )
            self.add_sentence_annotation()
            sentences=self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).select( self._config[ 'Annotation' ][ 'SENTENCE_TYPE' ] )
        
        #add token type annotation at correct location using automaton
        for sentence in sentences:
            text=sentence.get_covered_text().lower()
            for end_index, ( score, lemma, term ) in A.iter( text ):
                if not term:
                    continue
                start_index = end_index - (len(term) - 1)
                #check if detected term in text is not part of other token via is_token
                if is_token( start_index, end_index, text ):
                    self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).add_annotation( \
                     token_type( begin=sentence.begin+start_index, end=sentence.begin+end_index+1, score=SCORE, lemma=lemma, term=term ) )
                    
                    
    def add_named_entity_annotation( self, named_entities_sentences: List[ List[ Named_entity ] ] ):
        
        '''
        Add named entity annotations ( self._config[ 'Annotation' ][ 'NER_TYPE' ] ) to self.cas. Named entities should be provided via a List of List of named entities (Named_entity). Length of this list should be equal to the number of annotated sentences ( i.e. self._config[ 'Annotation' ][ 'SENTENCE_TYPE' ] )

        :param named_entities_sentences: List of List of Named_entity.
        '''
        
        #first check if AnnotationAdder contains _cas object:
        if not hasattr( self, 'cas' ):
            raise AttributeError( "AnnotationAdder should contain 'cas' attribute. Please create 'cas' attribute from text via the self.create_cas_from_text method(text), before using the self.add_sentence_annotation() method" )
            
        ner_type=self._typesystem.get_type(  self._config[ 'Annotation' ][ 'NER_TYPE' ] )

        #get the sentences:
        sentences=self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).select( self._config[ 'Annotation' ][ 'SENTENCE_TYPE' ] )
        if not sentences:
            print( "self.cas does not contain sentences ( SENTENCE_TYPE ). Adding sentence annotations via the .add_sentence_annotation() method." )
            self.add_sentence_annotation()
            sentences=self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).select( self._config[ 'Annotation' ][ 'SENTENCE_TYPE' ] )   
                
        #sanity check: for every annotated sentence, there should be a list of named entities provided.
        assert len( sentences ) ==len( named_entities_sentences ), "For every sentence (annotated via SENTENCE_TYPE) there should be exactly one list of detected named entities provided ( List[Named_entity])"
        
        for sentence, named_entities_sentence in zip( sentences, named_entities_sentences ):
            
            #for some sentences, it could be that no named_entities are found. I.e. List[Named_entity] is [].
            if not named_entities_sentence:
                continue
                
            for named_entity in named_entities_sentence:
                self.cas.get_view(self._config[ 'Annotation' ][ 'SOFA_ID' ]  ).add_annotation( \
                 ner_type( begin=sentence.begin+named_entity[2], \
                           end=sentence.begin+named_entity[3],\
                           value=named_entity[0],\
                           label=named_entity[1] ) )
                
                
    def add_contact_annotation( self, label='contact', root_type:str='PARAGRAPH_TYPE', merge_type:str='CONTACT_PARAGRAPH_TYPE'   ):
        
        '''
        Method to read paragraphs from the cas, check if the divType is labeled as label ( 'contact' ) by the sentence classifier. Merge consecutive such 'contact' paragraph, and annotate them with the 'CONTACT_PARAGRAPH_TYPE' ('merge_type') type. 
        
        :param named_entities_sentences: List of List of Named_entity.
        '''

        #first check if AnnotationAdder contains _cas object:
        if not hasattr( self, 'cas' ):
            raise AttributeError( "AnnotationAdder should contain 'cas' attribute. Please create 'cas' attribute from text via the self.create_cas_from_text method(text), before using the self.add_sentence_annotation() method" )
        
        contact_paragraph_type=self._typesystem.get_type(  self._config[ 'Annotation' ][ merge_type ] )

        #check if cas object already contains contact_paragraph annotations. If so remove them first
        contact_paragraph_annotations=self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ]  ).select( self._config[ 'Annotation' ][ merge_type ] )
        
        if contact_paragraph_annotations:
            print( "self.cas already contains CONTACT_PARAGRAPH_TYPE annotations. Removing these annotations, before adding new ones." )
            for contact_paragraph_annotations in contact_paragraph_annotations:
                self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ]  ).remove_annotation( contact_paragraph_annotations )
            
        #Get the paragraphs:
        paragraphs=self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).select( self._config[ 'Annotation' ][ root_type ]  )
    
        #Now check if the paragraph is labeled as contact by the sentence classifier for contact detection. 
        #If so merge them if they are consecutive, and annotate with 'contact_paragraph_type' annotation.
        in_contact=False
        for i,par in enumerate(paragraphs):
            #start of new 'contact' section
            if par.divType == label:
                if in_contact == False:
                    begin_index=par.begin
                    in_contact=True
                previous_contact_par=par

            if in_contact and par.divType!=label:
                end_index=previous_contact_par.end
                in_contact=False
                #get the cleaned text (removal of newlines)
                contact_paragraph_text=self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).sofa_string[ begin_index:end_index ]
                contact_paragraph_text="\n".join([ sentence.strip() for sentence in contact_paragraph_text.split( "\n" ) if sentence.strip()] )
                #add annotation
                self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).add_annotation( \
                contact_paragraph_type( begin = begin_index, end=end_index, divType=label, content=contact_paragraph_text ) )

            #special case when last paragraph in the cas is a contact
            if i==len( paragraphs )-1 and par.divType==label:
                end_index=par.end
                #get the cleaned text (removal of newlines)
                contact_paragraph_text=self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).sofa_string[ begin_index:end_index ]
                contact_paragraph_text="\n".join([ sentence.strip() for sentence in contact_paragraph_text.split( "\n" ) if sentence.strip()] )
                #add_annotation
                self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).add_annotation( \
                contact_paragraph_type( begin = begin_index, end=end_index, divType=label, content=contact_paragraph_text ) )
                
                
    def add_context(self, root_type:str='CONTACT_PARAGRAPH_TYPE' , type_to_add:str='SENTENCE_TYPE' ):
        
        '''
        Method to add context to root_type annotation. Method will get the covered type_to_add annotations that are covered by the root type, get the previous, and nex annotation of type_to_add type, and add the text they cover to the .content attribute of root_type annotation as .content_context attribute of the feature type.
        
        :param root_type: String.
        :param type_to_add: String.
        '''
        
        contact_paragraphs=self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).select( self._config[ 'Annotation' ][ root_type ]  )
        paragraphs=self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ]).select( self._config[ 'Annotation' ][ type_to_add ]  )
        
        for contact_paragraph in contact_paragraphs:
            covered_paragraphs=self.cas.get_view( self._config[ 'Annotation' ][ 'SOFA_ID' ] ).select_covered( self._config[ 'Annotation' ][ type_to_add ], contact_paragraph )
            
            if not covered_paragraphs:
                continue
            
            xmiID_begin=covered_paragraphs[0].xmiID
            xmiID_end=covered_paragraphs[-1].xmiID
            
            text=''
            for par in paragraphs:
                #add the paragraph preceding the contact paragraph as context
                if par.xmiID==xmiID_begin -1:
                    text=par.get_covered_text() + '\n'+ contact_paragraph.content

                #add the paragraph following the contact paragraph as context
                if par.xmiID==xmiID_end+1:
                    #case where we already prepended context to contact_paragraph.content
                    if text:
                        text=text + "\n" + par.get_covered_text()
                    #case where we did not already prepended context to contact_paragraph.content
                    else:
                        text=contact_paragraph.content + "\n" + par.get_covered_text()

                text="\n".join([ sentence.strip() for sentence in text.split( "\n" ) if sentence.strip()] )

            contact_paragraph.content_context=text.strip()  #the strip is probably not necessary..
            
    
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
    for i, sentence in enumerate( sentences ):
        
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
        
        if i==len( sentences )-1 and in_paragraph:
            paragraphs_index.append( ( start_position, position-1 ) )
            
    return paragraphs_index


def get_paragraphs_index_trafilatura( text:str )-> List[ Tuple[ int,int ] ]:
    
    '''
    Helper function to find offsets of the paragraphs in the json['text'] generated by trafilatura library. Paragraphs are obtained using text.split( "\n" ). If two consecutive paragraps are prepended by "- " they are considered belonging to the same paragraph by trafilatura library (i.e. they indicate an enumeration, or list in the trafilatura library, so we want them in the same paragraph).
    
    :param text: String. String, for instance results of tika parser.
    :return: List[ Tuple[ int, int ] ]. List with offsets of the paragraphs.
    '''
    
    paragraphs_index=[]
    
    position=0
    in_paragraph=False
    text=text.rstrip( "\n" )
    sentences=text.split( "\n" )

    for i,sentence in enumerate(sentences):
        if sentence:
            end_pos=position+len( sentence )
            #start of paragraph:
            if sentence[ :2 ] == '- ':
                if not in_paragraph:
                    in_paragraph=True
                    begin_pos_multiline=position
                #+1 to account for the "\n" (stripped via .split( "\n" ))
                position+=(len(sentence )+1)

            #end of paragraph
            if sentence[:2]!= '- ':
                if in_paragraph:
                    in_paragraph=False
                    #the paragraph
                    #(position -1 because we don't want the "\n" which is added in position+=(len(sentence )+1))
                    paragraphs_index.append( ( begin_pos_multiline, position-1 )  )
                    #the sentence following the paragraph (i.e. the current sentence)
                    paragraphs_index.append( ( position, end_pos ) )
                    #+1 to account for the "\n" (stripped via .split( "\n" ))
                    position+=(len(sentence )+1)
                else:
                    paragraphs_index.append( (position, end_pos) )
                    #+1 to account for the "\n" (stripped via .split( "\n" ))
                    position+=(len(sentence )+1)

            #last one (case were par is starting, or continuing to/in last line)
            if i==len( sentences ) -1 and sentence[:2]=='- ':
                paragraphs_index.append( ( begin_pos_multiline, end_pos ) )
        else:
            #to account for the 'empty' sentences ( i.e. "" ) (but should not be there with trafilatura)
            position+=1
        
    return paragraphs_index 