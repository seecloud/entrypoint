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

from __future__ import absolute_import

import json

from entrypoint.args import VARIABLES
from entrypoint import utils


CONF = {}

SERVICE_CONFIG_KEY = "/{service}/config"


def get_local_config():
    path = VARIABLES["config_file"]
    if not path:
        raise Exception(
            "Could not read configuration file because it was not specified.")
    with open(path) as f:
        return json.load(f)


@utils.retry
def get_remote_config():
    hosts = VARIABLES["etcd"]["endpoint"]
    if not hosts:
        raise Exception(
            "Could not connect to etcd because hosts were not specified")
    service_name = VARIABLES["service_name"]
    etcd_client = utils.get_etcd_client()
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
