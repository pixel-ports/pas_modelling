FROM ubuntu:18.04

RUN apt-get update && apt-get upgrade -y
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get install -yq wget tar xz-utils build-essential
RUN apt-get install -yq libncursesw5-dev libgdbm-dev libc6-dev zlib1g-dev libsqlite3-dev tk-dev libssl-dev openssl libffi-dev
RUN wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tar.xz
RUN tar xf Python-3.8.0.tar.xz
WORKDIR /Python-3.8.0
RUN ./configure
RUN make -j $(nproc) && make install
WORKDIR /

RUN python3.8 -m pip install pipenv

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /tmp
COPY ./Pipfile /tmp
COPY ./Pipfile.lock /tmp
RUN pipenv install --deploy --system  # Installs dependencies to the system without virtualenv

WORKDIR /pas
