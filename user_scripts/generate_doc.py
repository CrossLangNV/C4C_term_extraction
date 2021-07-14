def get_tags_from_sentence( NLP, sentence ):
    
    doc=NLP( sentence )
    
    dict_tags={}
    
    dict_tags['pos']=[]
    dict_tags['heads']=[]
    dict_tags['deps']=[]
    dict_tags['tags']=[]
    dict_tags[ 'ents' ]=[]
    
    for token in doc:
        dict_tags['pos'].append( token.pos_ )
        #head should be relative:
        head=token.head.i - token.i
        #if head < 0:
        #    head=0
        dict_tags[ 'heads' ].append( head )
        dict_tags[ 'deps' ].append( token.dep_ )
        dict_tags[ 'tags' ].append( token.tag_ )
    
    for ent in doc.ents:
        dict_tags['ents'].append( (ent.start, ent.end, ent.label  ) )
        
    return dict_tags

# doc=termextractor._nlp_dict[ 'en' ]( "Credit and mortgage account holders of the rich must submit their requests"  )