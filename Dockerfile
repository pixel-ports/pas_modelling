FROM ubuntu:18.04

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python3 python3-pip
RUN pip3 install pipenv

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /tmp
COPY ./Pipfile /tmp
COPY ./Pipfile.lock /tmp
RUN pipenv install --deploy --system  # Installs dependencies to the system without virtualenv

WORKDIR /pas
