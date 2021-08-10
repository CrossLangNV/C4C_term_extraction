# C4C Term extraction and named entity recognition

Instructions
------------

use "dbuild.sh" to build the docker image <br />
use "dcli.sh" to start a docker container


At `localhost:5001/docs`, one should find the ![swagger](https://github.com/CrossLangNV/C4C_term_extraction/tree/main/media/swagger.png?raw=true).

Now a json can be sent to `http://localhost:5001/extract_terms` or `http://localhost:5001/chunking`. The json should contain the fields `html` (i.e. scraped webpage) and `language`. The latter specifying which Spacy model to use. The following languages are supported: 'en', 'de', 'nl', 'fr', 'it', 'nb', 'sl', 'hr'.

For extraction of text, and removal of boilerplate text (extraction of main body text) the python package [trafilatura](https://github.com/adbar/trafilatura) is used. When specifying the language code, trafilatura will only extract text from webpages in the given language. If `http://localhost:5001/chunking` is used, it is not necessary to specify the language. 

The json could for example look like this:

```
input_json={}
input_json['html']="<title>The title </title><p>This the first test sentence.</p><p> And this is the second.</p><p> Another sentence </p><p> Now we start another paragraph </p><p>This is the third paragraph.</p>"
input_json['language']="en"
```

or 

```
input_json={}
input_json['html']="<title>The title </title><p>This the first test sentence.</p><p> And this is the second.</p><p> Another sentence </p><p> Now we start another paragraph </p><p>This is the third paragraph.</p>"
input_json['language']=""
```

if `http://localhost:5001/chunking` is used, and one is not interested in extracting text from webpages in a specific language.

Both `http://localhost:5001/extract_terms` and `http://localhost:5001/chunking` will return a json containing a "title", "tags", "excerpt", "text", "cas_content" and "language" field. The "cas_content" is a UIMA CAS object, encoded in base64.

In Python this base64 encoded UIMA CAS object can be decoded via:

```
import base64
decoded_cas=base64.b64decode( response_json['cas_content'] ).decode('utf-8')
```

The decoded Cas can then be loaded via the [dkpro-cassis](https://github.com/dkpro/dkpro-cassis) library.

```
from cassis.typesystem import load_typesystem
from cassis.xmi import load_cas_from_xmi

with open(os.path.join('media', 'typesystem.xml'), 'rb') as f:
    TYPESYSTEM = load_typesystem(f)
    
cas = load_cas_from_xmi(decoded_cas_content, typesystem=TYPESYSTEM, trusted=True)
```

The typesystem can be found at `media/typesystem.xml`

The base64 encoded UIMA Cas returned by the POST request to `http://localhost:5001/chunking` will contain a SOFA_ID view, and SENTENCE_TYPE annotation (see `media/TermExtraction.config`). A POST request to `http://localhost:5001/extract_terms` will add the same annotation, but also the TOKEN_TYPE and NER_TYPE annotations (terms and named entiies, see below).

## Example:

In `user_scripts/send_request.py` we provide various examples for posting requests to the API. One can run `send_request.py` from the command line `python3 send_request.py`. Detected annotations will be printed to the screen.

## 1) Chunking

Sentences/segments are detected. For this the posted `html` is processed by the `trafilatura` library, and the extracted text is added as a Sofa to a Cas object at the SOFA_ID view. Next sentences are annotated in this view via the SENTENCE_TYPE annotation. For more details we refer to the source code, and in particular to `src/annotations/annotations.py`, and the `.add_sentence_annotation(self,  )` method of the `AnnotationAdder` Class.

## 2) Term extraction


### Algorithm extraction of terms:
SpaCy's noun_chunk model is not available for all languages (see below). 
Therefore, the following 'automatic' noun chunks detection: 
```
>>> noun_chunks = {np for nc in doc.noun_chunks for np in [nc, doc[nc.root.left_edge.i:nc.root.right_edge.i + 1]]}
>>> noun_chunks = set([str(x) for x in doc.noun_chunks])
```
was substituded for the following approach:
```
>>> terms = []
>>> for token in doc:
...     if token.pos_ == 'NOUN' or token.pos_ == 'PROPN':
...         #this is the NOUN/PROPN:
...         terms.append( doc[token.i:token.i+1 ] )
...         #this is the right edge:
...         terms.append( doc[token.i:token.right_edge.i + 1] )
...         #this is right and left edge:
...         terms.append( doc[token.left_edge.i:token.right_edge.i + 1] )
...         #this is left edge:
...         terms.append( doc[token.left_edge.i: token.i + 1] )
```

Followed by an iterative cleaning of the resulting chunks.

#### Spacy models used per language:
- Dutch: SpaCy, noun chunks not supported
- German: SpaCy, noun chunks supported
- French: SpaCy, noun chunks supported (poor quality)
- Italian: SpaCy, noun chunks not supported
- Norwegian: SpaCy, noun chunks supported
- Croatian: [spacy_udpipe](https://github.com/TakeLab/spacy-udpipe), noun chunks not supported
- Slovenian: [spacy_udpipe](https://github.com/TakeLab/spacy-udpipe), noun chunks not supported

Detected terms are added as a TOKEN_TYPE annotation to the SOFA_ID view.

## 3) Named entity recognition (NER)

Using the above Spacy models, named entities are extracted. They are assigned one of the following labels:

        PERSON:      People, including fictional.
        NORP:        Nationalities or religious or political groups.
        FAC:         Buildings, airports, highways, bridges, etc.
        ORG:         Companies, agencies, institutions, etc.
        GPE:         Countries, cities, states.
        LOC:         Non-GPE locations, mountain ranges, bodies of water.
        PRODUCT:     Objects, vehicles, foods, etc. (Not services.)
        EVENT:       Named hurricanes, battles, wars, sports events, etc.
        WORK_OF_ART: Titles of books, songs, etc.
        LAW:         Named documents made into laws.
        LANGUAGE:    Any named language.
        DATE:        Absolute or relative dates or periods.
        TIME:        Times smaller than a day.
        PERCENT:     Percentage, including ”%“.
        MONEY:       Monetary values, including unit.
        QUANTITY:    Measurements, as of weight or distance.
        ORDINAL:     “first”, “second”, etc.
        CARDINAL:    Numerals that do not fall under another type.

Detected named entities are added as a NER_TYPE annotation to the SOFA_ID view.

