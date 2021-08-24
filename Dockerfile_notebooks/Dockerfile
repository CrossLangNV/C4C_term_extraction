#FROM tiangolo/uvicorn-gunicorn:python3.8
FROM nvidia/cuda:10.1-cudnn8-runtime-ubuntu18.04

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

EXPOSE 8888

VOLUME /notebook
WORKDIR /notebook

CMD ["jupyter", "notebook", "--no-browser", "--allow-root", "--ip='0.0.0.0'"]

#COPY ./app /app
