FROM ubuntu:18.04

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python3 python3-pip
RUN pip3 install pipenv

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN mkdir /pas
WORKDIR /pas

COPY ./Pipfile /pas
COPY ./Pipfile.lock /pas
RUN pipenv install --deploy --system  # Installs dependencies to the system without virtualenv

COPY ./ /pas/
