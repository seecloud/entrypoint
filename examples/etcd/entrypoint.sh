#!/bin/sh

ip="$(hostname -i)"

/usr/local/bin/etcd --listen-client-urls http://0.0.0.0:2379 --advertise-client-urls http://${ip}:2379 "$@"
