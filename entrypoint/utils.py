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

import functools
import logging
import operator
import time

import etcd

from entrypoint.args import VARIABLES

LOG = logging.getLogger(__name__)


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
