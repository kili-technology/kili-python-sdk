FROM ubuntu:18.04

RUN apt-get update && apt-get install -y locales

# Set the locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN apt-get update && apt-get install -y git python3 python3-pip build-essential

RUN pip3 install kili

RUN apt-get install -y swig

WORKDIR /app
ADD . /app

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "/app/entrypoint.sh" ]
