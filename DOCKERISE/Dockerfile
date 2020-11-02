FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get upgrade -y \
&& apt-get install -yq wget curl tar xz-utils build-essential \
#RUN apt-get install -yq libncursesw5-dev libgdbm-dev libc6-dev zlib1g-dev libsqlite3-dev tk-dev libssl-dev openssl libffi-dev #Legacy: VPN du service
&& wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tar.xz \
&& tar xf Python-3.8.0.tar.xz

WORKDIR /Python-3.8.0
RUN ./configure
#RUN make -j $(nproc) && make install
WORKDIR /

COPY . /pas_modelling
WORKDIR /pas_modelling
RUN pip install --requirement "./DOCKERISATION/requirements.txt"

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

#docker build -t pas_model -f ./DOCKERISE/Dockerfile . 