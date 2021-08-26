FROM nvidia/cuda:10.1-cudnn8-runtime-ubuntu18.04

ARG MODEL_DIR

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    curl && \
    apt-get clean
    
# Install miniconda to /miniconda
RUN curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

RUN conda install -y python=3.8 && \
conda install pytorch==1.7.0 cudatoolkit=10.1 -c pytorch && \
conda clean --all

#Install Cython
RUN apt-get update
RUN apt-get -y install --reinstall build-essential
RUN apt-get -y install gcc
RUN pip install Cython

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN apt-get update && apt-get -y install default-jre

RUN python -m nltk.downloader stopwords
RUN python -m spacy download 'nl_core_news_lg'
RUN python -m spacy download 'de_core_news_lg'
RUN python -m spacy download 'en_core_web_lg'
RUN python -m spacy download 'fr_core_news_lg'
RUN python -m spacy download 'it_core_news_lg'
RUN python -m spacy download 'nb_core_news_lg'

WORKDIR /work

#copy code:
COPY app.py /work
COPY src/annotations /work/src/annotations
COPY src/terms/ /work/src/terms
COPY src/cleaning /work/src/cleaning
COPY src/sentence_classification /work/src/sentence_classification
COPY src/aliases.py /work/src/

#copy model:
COPY $MODEL_DIR/*.bin /work/models/pytorch_model.bin
COPY $MODEL_DIR/config.json /work/models/
COPY $MODEL_DIR/vocab.txt /work/models/

#copy config files
COPY media/TermExtraction.config /work/media/
COPY media/typesystem.xml /work/media/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001"]