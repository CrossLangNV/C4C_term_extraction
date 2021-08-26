from typing import List, Union
import os
import time
import logging

from tqdm import tqdm, trange

from pathlib import Path

import torch
import numpy as np

from transformers import DistilBertTokenizerFast, BertTokenizerFast, AdamW
from transformers import DistilBertForSequenceClassification,BertForSequenceClassification
from transformers import WEIGHTS_NAME, CONFIG_NAME

from torch.nn import functional as F
from torch.utils.data import DataLoader

from sklearn.model_selection import train_test_split
#library for multi label stratified split:
from skmultilearn.model_selection import iterative_train_test_split
from sklearn.metrics import classification_report, accuracy_score

from .read_data import read_split, read_base64_multi_class_tsv, read_base64_multi_label_tsv
from .utils import clean_text, get_sample_weights_multi_class, get_sample_weights_multi_label

class PyTorchDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels=None, classification_type:str='multi_class' ):
        self.encodings = encodings
        if labels:
            self.labels = labels
        self.classification_type=classification_type

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        if hasattr( self, 'labels' ):
            if self.classification_type=='multi_class': #crossentropy loss needs a Long tensor as target
                item['labels'] = torch.tensor(self.labels[idx] )
            elif self.classification_type=='multi_label':
                item['labels'] = torch.tensor(self.labels[idx],dtype=torch.float)
        return item

    def __len__(self):
        return len( self.encodings['input_ids'] )

    
class TrainerBertSequenceClassifier( ):
    
    '''
    A trainer for BertForSequenceClassification model.
    '''
    
    def __init__( self, pretrained_model_name_or_path: str=None, model_type:str='BERT', classification_type:str='multi_class' ):
        
        '''
        :param pretrained_model_name_or_path: String. Path to a trained BertForSequenceClassification model, or model name with untrained classification layer.
        :param model_type: str. Model type (BERT of DISTILBERT)
        :param classification_type: str. Classification type (multi_label or multi_class)
        '''

        self._pretrained_model_name_or_path=pretrained_model_name_or_path
        
        if model_type not in [ 'BERT', 'DISTILBERT' ]:
            raise ValueError(f"Model type {model_type} not supported. Only 'BERT' and 'DISTILBERT' is supported.")
        self._model_type=model_type
        
        if classification_type not in [ 'multi_label', 'multi_class' ]:
            raise ValueError(f"Classification type {classification_type} not supported. Only 'multi_label' and 'multi_class' is supported.")
        self._classification_type=classification_type
        
    def load_model( self, num_labels:Union[ int, type(None) ]=None ):  
        
        '''
        Load a trained BertForSequenceClassification models, and accompanying BertTokenizer. Classification layers can be both trained or untrained.
        
        :param num_labels. Number of classes/labels for multi_class or multi_label classification problem.
        '''
        
        kwargs = dict( pretrained_model_name_or_path = self._pretrained_model_name_or_path ,\
                      num_labels=num_labels)
        kwargs={k: v for k, v in kwargs.items() if v is not None}

        if self._model_type=='BERT':
            self.model = BertForSequenceClassification.from_pretrained( **kwargs )
            self.tokenizer=BertTokenizerFast.from_pretrained( pretrained_model_name_or_path=self._pretrained_model_name_or_path )
            
        elif self._model_type=='DISTILBERT':
            self.model = DistilBertForSequenceClassification.from_pretrained( **kwargs )
            self.tokenizer=DistilBertTokenizerFast.from_pretrained( pretrained_model_name_or_path=self._pretrained_model_name_or_path )
            
    def train( self, path_data_dir: Path, output_dir:Path, index_first_relevant_column=0 , epochs=1, batch_size=16, learning_rate_adam=2e-5, val_size=0.1, weighted_sampling=False, class_weighting=False, cleaning=False, freeze_bert=False , gpu=0 ):
        
        #only change these parameters for the tokenizer if you know what you are doing:
        TRUNCATION=True
        PADDING=True
        MAX_LENGTH=512 #max length of sequences for tokenizer
        
        #weighted sampling only supported for multi-class problem:
        if weighted_sampling and self._classification_type=='multi_label':
            raise ValueError(  f"Weighted sampling is not supported for classification type {self._classification_type}. Please consider setting class_weighting to True for balanced training." )
        
        os.makedirs( output_dir , exist_ok=True )
        
        logging.basicConfig(filename= os.path.join( output_dir, "output.log" ) , level=logging.DEBUG)

        device = torch.device(f'cuda:{gpu}') if torch.cuda.is_available() else torch.device('cpu')

        #read the data from path:
        if Path( path_data_dir ).is_file():
            if os.path.splitext(os.path.basename( path_data_dir ))[-1]=='.tsv':
                if self._classification_type =='multi_label':
                    texts, labels, path=read_base64_multi_label_tsv( path_data_dir,  index_first_relevant_column = index_first_relevant_column )
                elif self._classification_type=='multi_class':
                    texts, labels, path=read_base64_multi_class_tsv( path_data_dir,  index_first_relevant_column = index_first_relevant_column )
            else:
                raise ValueError(f"File {path_data_dir} should be a tsv file. With first column base64 encoded text, and other columns containing the labels.")            
        else:
            texts, labels, path = read_split( path_data_dir )
            
        if self._classification_type=='multi_label':
            num_labels=len(labels[0])
            logging.info( f"Number of labels for {self._classification_type} classification task is {num_labels}." )
        elif self._classification_type=='multi_class':
            num_labels=len(np.unique( labels ))
            logging.info( f"Number of labels for {self._classification_type} classification task is {num_labels}." )
        
        #Whether to train only on cleaned training data.
        if cleaning:
        
            cleaned_train_texts=[]
            cleaned_train_labels=[]
            for text, label, path in zip(texts, labels, path ):
                cleaned_text=clean_text( text )
                if cleaned_text:
                    cleaned_train_texts.append( cleaned_text )
                    cleaned_train_labels.append( label )
                else:
                    logging.info( f"File at {path} is empty after cleaning. File will not be used for training of the classifier"  )
                    continue
        
        else:
            cleaned_train_texts=texts
            cleaned_train_labels=labels
            

        if not cleaned_train_texts:
            logging.info( f"Training dataset contains no documents after cleaning." )
            return
                
        if self._classification_type=='multi_class':
            #stratified split in training and validation sets, for multi-class we can use sklearn
            train_texts, val_texts, train_labels, val_labels = \
            train_test_split(cleaned_train_texts, cleaned_train_labels, test_size=val_size, stratify=cleaned_train_labels, random_state=2022 )
        elif self._classification_type=='multi_label':
            #stratified split in training and validation sets, for multi-label we should use the skmultilearn library
            train_texts, train_labels, val_texts, val_labels = \
            iterative_train_test_split(np.array( cleaned_train_texts ).reshape( len(cleaned_train_texts),1  ), \
                                       np.array(cleaned_train_labels), test_size=val_size  )
            train_texts=train_texts.flatten().tolist()
            val_texts=val_texts.flatten().tolist()
            train_labels=train_labels.tolist()
            val_labels=val_labels.tolist()
                
        if self._model_type=='BERT':
            #load Bert model with classification layers not trained:
            self.load_model(num_labels=num_labels )
            self.model.to(device)
            if freeze_bert:
                self.freeze_bert_encoder()
                self.unfreeze_bert_encoder_last_layers()
            
        elif self._model_type=='DISTILBERT':
            self.load_model( num_labels=num_labels )
            self.model.to(device)
            if freeze_bert:
                self.freeze_distilbert_encoder()
                self.unfreeze_distilbert_encoder_last_layers()
                    
        train_encodings = self.tokenizer(train_texts, truncation=TRUNCATION, padding=PADDING, max_length=MAX_LENGTH )
        val_encodings = self.tokenizer(val_texts, truncation=TRUNCATION, padding=PADDING, max_length=MAX_LENGTH )
        
        self.model.config.tokenizer_truncation=TRUNCATION
        self.model.config.tokenizer_padding=PADDING
        self.model.config.tokenizer_maxlength=MAX_LENGTH
        self.model.config.classification_type=self._classification_type

        train_dataset = PyTorchDataset(train_encodings, labels=train_labels, classification_type=self._classification_type )
        val_dataset = PyTorchDataset(val_encodings, labels=val_labels, classification_type=self._classification_type )

        if self._classification_type=='multi_class':
            weights, samples_weight=get_sample_weights_multi_class( train_labels )
        elif self._classification_type=='multi_label':
            weights, _=get_sample_weights_multi_label( train_labels )

        if not class_weighting:
            weights=None
        else:
            weights=weights.to(device)
        
        #weighted random sampling:
        #weighted sampling only supported for multi-class problem:
        if weighted_sampling and self._classification_type=='multi_class': 

            train_sampler = torch.utils.data.sampler.WeightedRandomSampler( samples_weight, len(samples_weight )  )
            train_dataloader = DataLoader(train_dataset, batch_size=batch_size, sampler=train_sampler)
            
        else:
            train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True )

        validation_dataloader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
                
        #set weight decay rate (regularization) for AdamW

        param_optimizer = list(self.model.named_parameters())
        no_decay = ['bias', 'gamma', 'beta']
        optimizer_grouped_parameters = [
            {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)],
             'weight_decay_rate': 0.01},  #0.01
            {'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)],
             'weight_decay_rate': 0.00}  #0.0
        ]
        
        optimizer = AdamW(optimizer_grouped_parameters, lr=learning_rate_adam, correct_bias=False)  

        start=time.time()
        
        #activation function and loss function:
        if self._classification_type=='multi_class':
            activation=torch.nn.Softmax(dim=1)
            self._loss_function=torch.nn.CrossEntropyLoss( weight = weights )
        elif self._classification_type=='multi_label':
            activation=torch.nn.Sigmoid()
            self._loss_function=torch.nn.BCEWithLogitsLoss(pos_weight=weights )

        # BERT training loop
        for epoch in trange(epochs, desc="Epoch"):  
            
            logging.info( f"Start training epoch {epoch+1}." )

            ## TRAINING

            # Set our model to training mode
            self.model.train()
            # Tracking variables
            tr_loss,tr_accuracy = 0,0
            nb_tr_steps = 0

            # Train the data for one epoch
            for step, batch in enumerate(train_dataloader):

                optimizer.zero_grad()
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                outputs = self.model(input_ids, attention_mask=attention_mask)
                logits=outputs[0]
                loss=self._loss_function( logits, labels )
                loss.backward()
                optimizer.step()
                tr_loss+=loss.item()
                labels_cpu=labels.to('cpu').numpy()
                pred_proba=activation( logits ).detach().to( 'cpu' ).numpy()       
                tmp_tr_accuracy=self.flat_accuracy( pred_proba, labels_cpu )
                tr_accuracy+=tmp_tr_accuracy
                nb_tr_steps+=1

            logging.info("Training Accuracy: {}".format(tr_accuracy/nb_tr_steps))
            logging.info("Train loss: {}".format(tr_loss/nb_tr_steps))

          ## VALIDATION
            
            logging.info( f"Evaluating epoch {epoch+1}." )

            # Put model in evaluation mode
            self.model.eval()
            # Tracking variables
            
            eval_loss, eval_accuracy = 0, 0
            nb_eval_steps = 0
            preds_proba=np.empty( (0, self.model.config.num_labels ), np.float32 )
            
            # Evaluate data for one epoch
            for batch in validation_dataloader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                with torch.no_grad():
                    outputs = self.model(input_ids, attention_mask=attention_mask)
                logits=outputs[0]
                loss=self._loss_function( logits, labels )
                labels_cpu=labels.to('cpu').numpy()
                eval_loss+=loss.item()
                pred_proba=activation( logits ).detach().to( 'cpu' ).numpy()
                tmp_eval_accuracy=self.flat_accuracy( pred_proba, labels_cpu )
                eval_accuracy+=tmp_eval_accuracy
                nb_eval_steps+=1
                preds_proba=np.append( preds_proba, pred_proba, axis=0 )

            if self._classification_type=='multi_class':
                preds_labels=np.argmax( preds_proba, axis=1 )
            elif self._classification_type=='multi_label':
                preds_labels = (np.array( preds_proba ) >= 0.5)*1
                     
            logging.info("Validation Accuracy: {}".format(eval_accuracy/nb_eval_steps))
            logging.info("Validation Loss: {}".format(eval_loss/nb_eval_steps))
            logging.info( "Classification report on validation set:" )
            logging.info( classification_report( val_labels, preds_labels  ))

 
        end=time.time()
        logging.info( f"Training took: {end-start}")
            
        logging.info( f"Saving trained model to {output_dir}" )
            
        output_model_file = os.path.join( output_dir, WEIGHTS_NAME)
        output_config_file = os.path.join( output_dir, CONFIG_NAME)

        torch.save(self.model.state_dict(), output_model_file)
        self.model.config.to_json_file(output_config_file)
        self.tokenizer.save_vocabulary(output_dir)
            
            
    def predict( self, documents:List[str], batch_size:int=16, label_empty_documents:int=0, cleaning=False ):
        
        '''
        Inference on set of documents using trained BertForSequenceClassification model.
        '''
        
        if not hasattr( self, 'model' ) or not hasattr( self, 'tokenizer' ):
            print( f"Loading { self._model_type} model finetuned for classification task from {self._pretrained_model_name_or_path }")
            self.load_model( )
        
        device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

        if hasattr( self.model.config, 'tokenizer_truncation' ):
            truncation=self.model.config.tokenizer_truncation
        else:
            print( f"Configuration file of trained BertSequenceClassifier loaded from {self._pretrained_model_name_or_path } does not contain 'tokenizer_truncation', falling back to default (truncation=True)" )
            truncation=True

        if hasattr( self.model.config, 'tokenizer_padding' ):
            padding = self.model.config.tokenizer_padding
        else:
            print( f"Configuration file of trained BertSequenceClassifier loaded from {self._pretrained_model_name_or_path} does not contain 'tokenizer_padding', falling back to default (padding=True)" )
            padding=True

        if hasattr( self.model.config, 'tokenizer_maxlength' ):
            max_length = self.model.config.tokenizer_maxlength
        else:
            print( f"Configuration file of trained BertSequenceClassifier loaded from {self._pretrained_model_name_or_path } does not contain 'tokenizer_maxlength', falling back to default (max_length=512)" )
            max_length=512
            
        if hasattr( self.model.config, 'classification_type' ):
            self._classification_type=self.model.config.classification_type
        else:
            print( f"Configuration file of trained BertSequenceClassifier loaded from {self._pretrained_model_name_or_path } does not contain 'classification_type', falling back to default: 'multi_class' " )
            self._classification_type='multi_class'
                    
        if self._classification_type=='multi_label' and isinstance( label_empty_documents, int ):
            label_empty_documents=self.model.config.num_labels*[ label_empty_documents ]
            print( f"Assigned label for empty documents (after cleaning) will be {label_empty_documents}" )
            
        #cleaning of the documents:
        if cleaning:
            cleaned_documents=[]
            indices_non_empty_documents=[]
            for i,document in enumerate(documents):
                cleaned_document=clean_text( document )
                #empty documents after cleaning should not be processed via the classifier:
                if cleaned_document:
                    indices_non_empty_documents.append( i )
                    cleaned_documents.append( cleaned_document )
        else:
            cleaned_documents=documents
            indices_non_empty_documents=list(range(len( documents )))
            
        #case if all documents are empty after cleaning
        if not cleaned_documents:
            preds_labels_all=[]
            preds_proba_all=[]
            
            for i in range( len(documents) ):

                preds_labels_all.append( label_empty_documents )
                preds_proba_all.append( [ -1.0 ]*self.model.config.num_labels  )
            
            return np.array(preds_labels_all), np.array( preds_proba_all )

        test_encodings = self.tokenizer(cleaned_documents, truncation=truncation, \
                                                           padding=padding, max_length=max_length)

        test_dataset = PyTorchDataset(test_encodings, labels=None, classification_type=self._classification_type )
        
        #activation function:
        if self._classification_type=='multi_class':
            activation=torch.nn.Softmax(dim=1)         
        elif self._classification_type=='multi_label':
            activation=torch.nn.Sigmoid()
         
        # Put model in evaluation mode
        self.model.eval()
        self.model.to(device)

        test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

        preds_proba=np.empty( (0, self.model.config.num_labels ), np.float32 )

        # Inference
        for batch in test_dataloader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)

            with torch.no_grad():
                outputs = self.model(input_ids, attention_mask=attention_mask )

            preds_proba=np.append( preds_proba, activation( outputs[0] ).to( 'cpu' ).numpy(), axis=0  )

        if self._classification_type=='multi_class':
            preds_labels=np.argmax( preds_proba, axis=1 )
        elif self._classification_type=='multi_label':
            preds_labels = (np.array( preds_proba ) >= 0.5)*1
        
        assert len( preds_labels ) == len( preds_proba ) == len( cleaned_documents )
        
        #assign empty documents, possibly after cleaning, the label 'label_empty_documents'.
        preds_labels_all=[]
        preds_proba_all=[]
        for i in range( len( documents  )  ):
            if i in indices_non_empty_documents:
                preds_labels_all.append( preds_labels[ indices_non_empty_documents.index(i) ] )
                preds_proba_all.append( preds_proba[ indices_non_empty_documents.index(i) ].tolist() )
            else:
                preds_labels_all.append( label_empty_documents )
                preds_proba_all.append( [ -1.0 ]*self.model.config.num_labels  )
        
        return np.array(preds_labels_all), np.array( preds_proba_all )
    
    def freeze_distilbert_encoder( self ):
        for param in self.model.distilbert.parameters():
            param.requires_grad = False

    def unfreeze_distilbert_encoder_last_layers( self ):
        for name, param in self.model.distilbert.named_parameters():
            if "layer.5" in name or "pooler" in name:
                param.requires_grad = True

    def freeze_bert_encoder( self ):
        for param in self.model.bert.parameters():
            param.requires_grad = False           

    def unfreeze_bert_encoder_last_layers( self ):
        for name, param in self.model.bert.named_parameters():
            if "encoder.layer.11" in name or "pooler" in name:
                param.requires_grad = True 
            
    def flat_accuracy(self, preds, labels, threshold=0.5):
        if self._classification_type=='multi_class':
            outputs=np.argmax( preds, axis=1 ).flatten()
        elif self._classification_type=='multi_label': 
            outputs = np.array(preds) >= threshold
        return accuracy_score(labels, outputs)