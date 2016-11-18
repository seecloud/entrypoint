FROM ubuntu:xenial

RUN apt-get update \
    && apt-get install -y python-setuptools python-pbr git-core python-jsonschema python-etcd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /opt/
WORKDIR /opt/

RUN python setup.py install \
    && apt-get remove --auto-remove -y git-core \
    && rm -rf /opt

WORKDIR /
