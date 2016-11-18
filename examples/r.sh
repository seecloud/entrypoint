#!/bin/bash -ex

dockip() {
    docker inspect --format '{{ .NetworkSettings.IPAddress }}' $1
}

etcd_ip=$(dockip etcd)
docker run --rm -ti \
            --env SERVICE_NAME=service-a \
            --env ENVIRONMENT=etcd \
            --env ETCD_HOSTS=$etcd_ip:2379 \
            entry_service:latest \
            bash
