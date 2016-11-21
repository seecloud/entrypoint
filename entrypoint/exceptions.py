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


class EndpointIsNotRegistered(Exception):
    message = "Service {service_name} does not have registered endpoint " \
              "for the type {endpoint_type}"

    def __init__(self, service_name, endpoint_type):
        super(EndpointIsNotRegistered, self).__init__(self.message.format(
            service_name=service_name,
            endpoint_type=endpoint_type,
        ))
