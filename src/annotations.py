from typing import List, Tuple

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
    Helper function to find offsets of the paragraphs in a string (paragraphs are considered blockes of sentences (text.strip( "\n" )) for which sentence.strip() is not None.
    
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