FROM python:3.11-alpine

RUN apk --no-cache upgrade && apk --no-cache add tzdata

RUN addgroup usergroup && adduser -D user -G usergroup && mkdir /work
WORKDIR /work

ADD requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

ADD cleaner ./cleaner

USER user
ENTRYPOINT PYTHONUNBUFFERED=1 python cleaner/main.py