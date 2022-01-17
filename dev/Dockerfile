# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /work

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN python3 -m nltk.downloader punkt averaged_perceptron_tagger maxent_ne_chunker words

RUN apt-get update
RUN apt-get install -y git curl autoconf automake libtool python-dev pkg-config
RUN apt install build-essential -y --no-install-recommends
RUN git clone https://github.com/openvenues/libpostal
RUN cd libpostal; make distclean ; ./bootstrap.sh; ./configure --datadir=/tmp/libpostal_data ; make -j4 ; make install

RUN ldconfig

RUN pip3 install postal

RUN pip3 install numpy



