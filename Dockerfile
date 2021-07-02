FROM tiangolo/uvicorn-gunicorn:python3.8
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN python -m nltk.downloader stopwords
RUN python -m spacy download 'nl_core_news_lg'
RUN python -m spacy download 'de_core_news_lg'
RUN python -m spacy download 'en_core_web_lg'
RUN python -m spacy download 'fr_core_news_lg'
RUN python -m spacy download 'it_core_news_lg'
RUN python -m spacy download 'nb_core_news_lg'

COPY ./app /app