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

import collections
import json
import logging

from six.moves import urllib

import etcd

from entrypoint import exceptions
from entrypoint import utils

LOG = logging.getLogger(__name__)

SERVICE_ENDPOINTS_KEY = "/{service}/endpoints"

_Endpoint = collections.namedtuple("Endpoint", (
    "protocol",
    "address",
    "port",
))


class Endpoint(_Endpoint):
    __slots__ = ()

    def url(self, default_protocol="http", default_path="/"):
        url = urllib.parse.urlunsplit((
            self.protocol or default_protocol,
            "{0}:{1}".format(self.address, self.port),
            default_path,
            "", "",
        ))
        return url


@utils.retry
def get_endpoint(service_name, endpoint_type="private"):
    etcd_client = utils.get_etcd_client()
    endpoints_key = SERVICE_ENDPOINTS_KEY.format(service=service_name)
    try:
        endpoints_record = etcd_client.get(endpoints_key)
        endpoints = json.loads(endpoints_record.value)
        endpoint = endpoints[endpoint_type]
    except etcd.EtcdKeyNotFound:
        LOG.error("Could not find the service %s/%s in etcd.",
                  service_name, endpoint_type)
        raise exceptions.EndpointIsNotRegistered(service_name, endpoint_type)
    except KeyError:
        LOG.error("Could not find the service %s/%s in etcd: %s",
                  service_name, endpoint_type, endpoints)
        raise exceptions.EndpointIsNotRegistered(service_name, endpoint_type)
    else:
        record = Endpoint(
            protocol=endpoint.get("protocol"),
            address=endpoint.get("address"),
            port=endpoint.get("port"),
        )
        return record
