FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get -y install netcat &&  apt-get -y install gettext

RUN mkdir /code

COPY . /code/
RUN pip install -r /code/requirements/dev.txt
WORKDIR /code
