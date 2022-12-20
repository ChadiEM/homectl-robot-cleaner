FROM python:3.11-alpine

RUN apk upgrade && apk add tzdata

RUN addgroup usergroup && adduser -D user -G usergroup && mkdir /work
WORKDIR /work

ADD requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

ADD *.py ./
ADD conditions ./conditions/

USER user
ENTRYPOINT PYTHONUNBUFFERED=1 python main.py