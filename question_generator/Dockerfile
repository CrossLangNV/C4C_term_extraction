FROM nvidia/cuda:10.1-cudnn8-runtime-ubuntu18.04

MAINTAINER arne <arnedefauw@gmail.com>

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
conda install flask==1.1.2 && \
conda install pytorch==1.7.0 cudatoolkit=10.1 -c pytorch && \
conda clean --all

#Install Cython
RUN apt-get update
RUN apt-get -y install --reinstall build-essential
RUN apt-get -y install gcc
RUN pip install Cython

RUN pip install \
transformers==3.4.0

RUN apt-get -y update
RUN apt-get -y install git

RUN git clone https://github.com/amontgomerie/question_generator
RUN python -m pip install -e question_generator

# create root directory for our project in the container
RUN mkdir /project
# Set the working directory to e.g. /project
WORKDIR /project
