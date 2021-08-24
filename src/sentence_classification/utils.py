from typing import List, Tuple
import string
import re

import torch
import numpy as np
from collections import Counter

def clean_text( text:str, minumum_sentence_length: int=6, exclude_pattern: bool=True )->str:
    
    '''
    Function to clean text. Text will be split in segments using newlines and tabs. Sentences with minimum sentence \
    length le minimum_sentence_length will be removed. Sentences matching the pattern, when exlude_pattern=True, will \
    also be removed. Segments are concatenated using newlines and returned.
    
    :param text: str. Input text to be cleaned.
    :param minimum sentence length: str. Minimum sentence length.
    :param exclude_pattern: bool. Whether to exclude sentences matching the pattern.
    :return: str. Cleaned text.
    '''
    
    extra_chars_to_exclude=[ '∙', ' ', "—", "…", "·", "+", "“", "√" , "≤", "<",'≥', ">" ,"⋅", "■", "£", "½", "÷","«","°", "»", "–", "†", "‡" ]  

    #exclude sentences matching this pattern ( i.e. sentences consisting only of numericals / punctuation )
    punctuation_chars=string.punctuation+"".join( extra_chars_to_exclude)
    pattern = re.compile("[0-9{}]+$".format(re.escape( punctuation_chars )))

    split_text=[]
    for sentence in text.split( "\n" ):
        split_text.extend( sentence.split( "\t" )  )

    cleaned_text=[]
    for sentence in split_text:
        sentence=sentence.strip()
        if not sentence:
            continue
        if len(sentence.split())<=minumum_sentence_length:
            continue
        if exclude_pattern and pattern.match( sentence ):
            continue
        else:
            cleaned_text.append( sentence  )
    return "\n".join(cleaned_text).strip()

def get_sample_weights_multi_class( labels: List[int] )->Tuple[torch.Tensor, torch.Tensor]:
    
    class_ids=np.unique( labels )
    counts=Counter(  labels )
    class_sample_count=[counts[ class_id ] for class_id in class_ids]

    weights=1 / torch.Tensor(class_sample_count)
    samples_weight=np.array([weights.double()[label] for label in labels])

    samples_weight = torch.from_numpy(samples_weight)
    
    return weights, samples_weight

def get_sample_weights_multi_label( labels: List[ List[int] ]  )-> Tuple[torch.Tensor, type(None)]:
    
    labels = torch.FloatTensor(labels )
    weights=labels.shape[0]/torch.sum( labels, dim=0 ) -1
    #weights=weights/torch.max( weights )
    samples_weight=None
    return weights, samples_weight
