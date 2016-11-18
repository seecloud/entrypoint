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

import json
import logging
import os

from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer

import entrypoint
from entrypoint import config

CONF = config.CONF

SERVICE_NAME = os.environ.get("SERVICE_NAME", "service")
DEFAULT_CONF = "/etc/conf.json"
DEFAULT_PORT = 8000

entrypoint.process_entrypoint(SERVICE_NAME, default_config_path=DEFAULT_CONF)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        json.dump(CONF, self.wfile)


def main():
    log_datefmt = "%Y-%m-%d %H:%M:%S"
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=log_format, datefmt=log_datefmt)
    port = CONF.get("port", DEFAULT_PORT)
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

if __name__ == "__main__":
    main()
