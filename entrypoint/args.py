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

import argparse
import logging
import os
import re

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

VARIABLES = {}


def process_arguments(service_name, default_config_path=None):
    global VARIABLES

    parser = argparse.ArgumentParser(add_help=False)
    parser = register_arguments(parser, service_name,
                                default_config_path=default_config_path)
    args = parser.parse_args()

    VARIABLES["environment"] = args.environment
    VARIABLES["service_name"] = args.service_name
    VARIABLES["config_file"] = args.config_file
    VARIABLES["etcd"] = {
        "endpoint": args.etcd_hosts,
        "attempts": args.etcd_attempts,
        "attempts_delay": args.etcd_attempts_delay,
    }

    return parser


def register_arguments(parser, service_name, default_config_path=None):
    service_prefix = create_safe_prefix(service_name)
    parser.set_defaults(service_name=service_name)
    parser.add_argument(
        "--environment",
        metavar="ENVIRONMENT",
        choices=("etcd", "local"),
        default=os.environ.get("ENVIRONMENT", "local"),
        help="The type of the environment, can be etcd or local.",
    )
    default_hosts = get_default_etcd_hosts("ETCD_HOSTS", None)
    parser.add_argument(
        "--etcd-hosts",
        metavar="HOST:PORT",
        type=parse_hosts,
        nargs="+",
        default=default_hosts,
        help="A list of etcd hosts pairs, can be set by MS_ETCD_HOSTS. "
             "(types: HOST=STR, PORT=INT)",
    )
    parser.add_argument(
        "--etcd-attempts",
        type=int,
        default=os.environ.get("ETCD_ATTEMPTS", 10),
        help="Number of attempts to connect to etcd, can be set by "
             "ETCD_ATTEMPTS.",
    )
    parser.add_argument(
        "--etcd-attempts-delay",
        type=int,
        default=os.environ.get("ETCD_ATTEMPTS_DELAY", 6),
        help="Delay between etcd connection attempts, can be set by "
             "ETCD_ATTEMPTS_DELAY.",
    )
    parser.add_argument(
        "--config-file",
        metavar="PATH",
        default=os.environ.get(service_prefix("CONFIG_FILE"),
                               default_config_path),
        help="Path to a configuration file, can be set by MS_CONFIG_FILE.",
    )
    return parser


def get_default_etcd_hosts(env_var, default):
    if env_var in os.environ:
        hosts_str = os.environ[env_var].split(" ")
        hosts = list(map(parse_hosts, hosts_str))
        return hosts
    return default


def create_safe_prefix(service_name):
    assert re.match(r"^[a-zA-Z][-\w]*$", service_name), \
        "service_name have to start from letter and can contain letters, " \
        "numbers, dashes and underscores"
    prefix = service_name.upper().replace("-", "_")

    def add_prefix(string):
        return "{0}_{1}".format(prefix, string)
    return add_prefix


def parse_hosts(string):
    host, _, port = string.partition(":")
    return {"address": host, "port": int(port)}


def main():
    log_datefmt = "%Y-%m-%d %H:%M:%S"
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=log_format, datefmt=log_datefmt)
    process_arguments("entrypoint")
