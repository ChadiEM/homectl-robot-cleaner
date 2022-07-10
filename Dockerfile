FROM python:3.10-alpine

RUN apk upgrade && apk add nmap tzdata

RUN addgroup usergroup && adduser -D user -G usergroup && mkdir /work
WORKDIR /work

ADD requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

ADD *.py conditions ./

USER user
ENTRYPOINT PYTHONUNBUFFERED=1 python main.py