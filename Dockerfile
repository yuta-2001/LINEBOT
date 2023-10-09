FROM python:3.8

WORKDIR /usr/src/app

COPY /app/requirements.txt ./

RUN pip install --upgrade pip && \
    pip install -r requirements.txt
