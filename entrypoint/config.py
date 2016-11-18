# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import functools
import json
import logging
import operator
import time

import etcd

from entrypoint.args import VARIABLES

LOG = logging.getLogger(__name__)

CONF = {}

SERVICE_CONFIG_KEY = "/{service}/config"
SERVICE_STATUS_KEY = "/{service}/status"
SERVICE_ENDPOINTS_KEY = "/{service}/endpoints"


def retry(f):
    @functools.wraps(f)
    def decorate(*args, **kwargs):
        attempts = VARIABLES["etcd"]["attempts"]
        attempts_delay = VARIABLES["etcd"]["attempts_delay"]
        for i in range(attempts):
            try:
                return f(*args, **kwargs)
            except etcd.EtcdException as e:
                LOG.warning("Etcd fails with error on attempt %s/%s: %s",
                            i, attempts, str(e))
            time.sleep(attempts_delay)
        return f(*args, **kwargs)
    return decorate


@retry
def get_etcd_client():
    hosts = list(map(operator.itemgetter("address", "port"),
                     VARIABLES["etcd"]["endpoint"]))
    hosts_str = ",".join("{0}:{1}".format(*host) for host in hosts)
    LOG.debug("Using the following etcd hosts: %s", hosts_str)
    client = etcd.Client(host=tuple(hosts), allow_reconnect=True,
                         read_timeout=5)
    return client


def get_local_config():
    path = VARIABLES["config_file"]
    if not path:
        raise Exception(
            "Could not read configuration file because it was not specified.")
    with open(path) as f:
        return json.load(f)


@retry
def get_remote_config():
    hosts = VARIABLES["etcd"]["endpoint"]
    if not hosts:
        raise Exception(
            "Could not connect to etcd because hosts were not specified")
    service_name = VARIABLES["service_name"]
    etcd_client = get_etcd_client()
    key = SERVICE_CONFIG_KEY.format(service=service_name)
    config = etcd_client.get(key).value
    return json.loads(config)


def setup_config(validation_schema=None):
    global CONF
    environment = VARIABLES["environment"]
    if environment == "etcd":
        conf = get_remote_config()
    elif environment == "local":
        conf = get_local_config()
    else:
        raise Exception("Unknown environment type: {0}".format(environment))
    CONF.update(conf)
    return CONF
