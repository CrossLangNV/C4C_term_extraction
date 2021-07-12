from typing import List

def is_token(start_index:int, end_index:int, text:str, special_characters:List[str]=[ "-","_","+"]) -> bool:
    
    '''
    Given a start index, and end_index, and a string, this function checks if token(s) covered by the span is part of other token(s).
    
    :param start_index: int.
    :param end_index: int. 
    :param special_characters: List. List of special characters treated as alpha characters
    :return: bool.
    '''
    
    if start_index <0 or end_index<0:
        raise ValueError(f"Both start_index and end_index should be >0, however start_index is {start_index} and end_index is {end_index}")

    elif end_index<start_index:
        raise ValueError(f"end_index should be > start_index, however start_index is {start_index} and end_index is {end_index}")
        
    elif end_index > (len( text ) -1) :   #this one also takes care of no text case
        raise ValueError(f"end_index should be < len(text) -1, however end_index is {end_index} and len(text) is {len(text)}")
 
    #set of special characters treated as alpha characters
    #e.g.: the term 'livestock' in 'some livestock-some some' should not be annotated, but 'livestock' in 'some "livestock" some' should.
    special_characters=set(special_characters)
        
    #trivial case (start_index equal to end_index)
    #if start_index==end_index:
        #return False
    
    #e.g. 'livestock' in 'livestock'
    if start_index == 0 and end_index == len( text ) - 1:
        return True
    
    #e.g. 'livestock' in 'livestock some'
    elif start_index == 0:
        if (text[ end_index+1 ].isalpha() or text[ end_index+1 ] in special_characters ):
            return False
        
    #e.g. 'livestock' in 'some livestock'
    elif end_index == len( text ) -1:
        if (text[start_index -1].isalpha() or text[start_index -1] in special_characters ):
            return False
        
    #e.g. 'livestock' in 'some livestock some';      
    else:
        if (text[ start_index-1 ].isalpha() or text[ start_index-1 ] in special_characters ) \
        or (text[end_index+1].isalpha() or text[end_index+1] in special_characters ):
            return False
        
    return True