FROM python:3.8-slim-buster

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

## Install some basic utilities
#RUN apt-get update && apt-get install -y \
#    curl \
#    git && \
#    apt-get clean

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

WORKDIR /work

#copy code:
COPY main.py /work

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "1234"]
