FROM python:3.8-slim-buster

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

## Install some basic utilities
#RUN apt-get update && apt-get install -y \
#    curl \
#    git && \
#    apt-get clean

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN python3 -m nltk.downloader punkt

WORKDIR /work

#copy code:
COPY main.py /work

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "1234"]
