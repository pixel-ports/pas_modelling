FROM ubuntu:18.04

RUN apt-get update && apt-get upgrade -y
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get install -yq wget curl tar xz-utils build-essential
RUN apt-get install -yq libncursesw5-dev libgdbm-dev libc6-dev zlib1g-dev libsqlite3-dev tk-dev libssl-dev openssl libffi-dev
RUN wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tar.xz
RUN tar xf Python-3.8.0.tar.xz
WORKDIR /Python-3.8.0
RUN ./configure
RUN make -j $(nproc) && make install
WORKDIR /

COPY . /pas_modelling
WORKDIR /pas_modelling
RUN python3.8 -m pip install requests jsonschema elasticsearch==7.5.1

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8