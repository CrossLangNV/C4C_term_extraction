# c4concepts
## Instructions
This app currently extracts terms from the c4c data stored in solr, and returns a list that contains metadata per document, e.g. examples/example_output.json

To build a Docker image run:
```
docker build . -t c4concepts
```
To run the app:
```
docker run -d --name $mycontainer -p 80:80 c4concepts
```
To post a request use:
```
http://0.0.0.0:80/c4concepts
```
Or you can run the app locally:
```
uvicorn main:app --reload
```
You should post a json (see example.json) with the keys: "gemeente", "max_number_of_docs", "max_ngram_length", "language_code" , "auth_key" and "auth_value". 
The authorisation parameters could also be given via Postman, but this version will support manual input.  
Make sure that the data of the required 'gemeente' has been scraped, and is stored in solr.
The parameter max_number_of_docs was added to avoid iterating over all the data each time the app is launched.
The parameter max_ngram_length is self-explanatory.

## TODO
- Add device parameter ('cpu' or 'cuda:0')
- Relation extraction annotation

## Procedures detection:
We make use of a pretrained multilingual BERT model to detect segments that contain procedures.
The model currently supports DE/NL/FR, other languages t.b.a.

## POS-taggers per language:
- Dutch: SpaCy, noun chunks not supported
- German: SpaCy, noun chunks supported
- French: SpaCy, noun chunks supported (poor quality)
- Italian: SpaCy, noun chunks not supported
- Norwegian: SpaCy, noun chunks supported
- Croatian: [spacy_udpipe](https://github.com/TakeLab/spacy-udpipe), noun chunks not supported
- Slovenian: [spacy_udpipe](https://github.com/TakeLab/spacy-udpipe), noun chunks not supported

## Relation extraction:
At the moment, we are able to extract two related entities on the sentence level. This module will further be expanded.

## Differences between rule-based approach and the noun chunks:
SpaCy's noun_chunk model is not available for all languages. 
Therefore, a comparative analysis was conducted between the automatic noun chunks detection: 
```
>>> noun_chunks = {np for nc in doc.noun_chunks for np in [nc, doc[nc.root.left_edge.i:nc.root.right_edge.i + 1]]}
>>> noun_chunks = set([str(x) for x in doc.noun_chunks])
```
and the rule-based approach:
```
>>> noun_phrases = set()
>>> for token in doc:
...     if token.pos_ == ('NOUN' or 'PROPN'):
...         noun_phrases.add(token.text.strip())
...         noun_phrases.add(doc[token.left_edge.i:token.right_edge.i + 1].text.strip())
...         noun_phrases.add(doc[token.left_edge.i: token.i + 1].text.strip())
```
The later approach has demonstrated improved performance:
```
>>> len(noun_chunks)
39
>>> len(noun_phrases)
59
>>> noun_chunks.difference(noun_phrases)
set()
>>> noun_phrases.difference(noun_chunks)
{'trading', 'fragmentation', 'playing', 'transactions', 'level', 'instruments', 'discovery', 'allowances', 'price', 'field', 'internalisers', 'emission', 'markets', 'price discovery', 'facilities', 'degree', 'products', 'finance', 'process', 'venues'}
```
The processed text can be found in example.txt
