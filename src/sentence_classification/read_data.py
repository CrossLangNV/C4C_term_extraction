from pathlib import Path
from typing import List, Tuple
import pandas as pd
import base64

def read_split(split_dir: Path, class_names:List[str]=["neg", "pos"]) -> Tuple[List[str],List[int],List[str]]:
    
    '''
    Function to read text files from directory.
    
    :param split_dir: Path. Path to data directory. Directory structure should be split_dir/class_names[i], with split_dir/class_names[i] containing text files belonging to class i.
    :param model_type: List. List of class_names. class_names[0] will be label 0, class_names[1] label 1,...
    :return: 3 lists. Text content, labels and path to content. 
    '''
    
    split_dir = Path(split_dir)
    texts = []
    labels = []
    text_paths=[]
    for label_dir in class_names:
        for text_file in (split_dir/label_dir).iterdir():
            if text_file.is_file():
                texts.append(text_file.read_text())
                labels.append( class_names.index( label_dir ) )
                text_paths.append( text_file )
            
    return texts, labels, text_paths

def read_base64_multi_label_tsv( data_path: Path , index_first_relevant_column: int=0 ) -> Tuple[List[str],List[List[int]],List[str]] :
    
    '''
    Function to read data in tsv format for multi-label classification task. 
    
    :param data_path: Path. Path to a tsv file. With first column (or index_first_relevant_column) base64 encoded text, and other columns containing the labels (one-hot encoded).
    :first_relevant_column: int. Index of first relevant column (base64 encoded text). Columns at indices<index_first_relevant_column will be discarded.
    :return: 3 lists. Text content, labels and path to content. 
    '''
        
    def concat_labels(row, nr_of_columns):
        labels=[]
        for nr in range(index_first_relevant_column+1,nr_of_columns):
            labels.append( row[ nr ] )
        return labels
    
    #get the text:
    print( f"Reading tsv file for multi-label classification {data_path}" )
    data=pd.read_csv(  data_path, sep='\t' , header=None )
    len_before_dropna=data.shape[0]
    data.dropna( inplace=True )
    print(  f"Dropped {len_before_dropna - data.shape[0] } rows because they contained NaN's." )
    data[index_first_relevant_column]=data[index_first_relevant_column].apply( decode )
    
    texts=data[index_first_relevant_column].tolist()
    
    #get the labels
    data['labels']=data.apply( lambda row: concat_labels(row, data.shape[1]  ), axis=1 )

    labels=data['labels'].tolist()

    text_paths=[]
    for i in range( len(texts) ):
        text_paths.append( f"{data_path}_row{i}" )
    
    return texts, labels, text_paths


def read_base64_multi_class_tsv( data_path: Path, index_first_relevant_column: int=0 ) -> Tuple[List[str],List[int],List[str]]:
    
    '''
    Function to read data in tsv format for multi-class classification task. 
    
    :param data_path: Path. Path to a tsv file. With first column (or index_first_relevant_column) base64 encoded text, and other columns containing the label (in format 0,1,2,3...).
    :first_relevant_column: int. Index of first relevant column (base64 encoded text). Columns at indices<index_first_relevant_column will be discarded.
    :return: 3 lists. Text content, labels and path to content. 
    '''
    
    #get the text:
    print( f"Reading tsv file for multi-class classification {data_path}" )
    data=pd.read_csv(  data_path, sep='\t' , header=None )
    len_before_dropna=data.shape[0]
    data.dropna( inplace=True )
    print(  f"Dropped {len_before_dropna - data.shape[0] } rows because they contained NaN's." )

    data[index_first_relevant_column]=data[index_first_relevant_column].apply( decode )
    
    texts=data[index_first_relevant_column].tolist()
    labels=data[index_first_relevant_column+1].tolist()
    
    text_paths=[]
    for i in range( len(texts) ):
        text_paths.append( f"{data_path}_row{i}" )
    
    return texts, labels, text_paths

def decode( base64_encoded_string:str ) ->str:
    return  base64.b64decode(  base64_encoded_string ).decode( 'utf-8' )