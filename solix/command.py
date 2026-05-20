"""
   Copyright 2025 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import json
import typing

import mgw_dc

from solix.services.raw_command import handle_raw_command
from solix.services.raw_event import handle_raw_event
from util import conf, get_logger, MQTTClient
from util.device_manager import DeviceManager
from api import api

logger = get_logger(__name__.split(".", 1)[-1])

__all__ = ("Command",)

command_handlers = {}


class Command:
    def __init__(self, mqtt_client: MQTTClient, device_manager: DeviceManager, anker_solix_api: api.AnkerSolixApi):
        self.mqtt_client = mqtt_client
        self.device_manager = device_manager
        self._anker_solix_api = anker_solix_api

    async def execute_command(self, device_id: str, service: str, payload: typing.AnyStr, is_event: bool = False):
        logger.debug(device_id)
        if not is_event:
            payload = json.loads(payload)
            command_id = payload["command_id"]
            if len(payload["data"]) == 0:
                payload = {}
            else:
                payload = json.loads(payload["data"])
        elif payload is None:
            payload = {}
        if device_id not in self.device_manager.get_devices():
            logger.error("Undiscovered device " + device_id)
        try:
            if service in command_handlers:
                handler = command_handlers[service]
            else:
                if is_event:
                    handler = handle_raw_event
                else:
                    handler = handle_raw_command
            result = await handler(self.device_manager.get_devices()[device_id], anker_solix_api=self._anker_solix_api, payload=payload, service=service)
        except Exception as ex:
            logger.error("Command failed: {}".format(ex))
            return
        if is_event:
            response = result
            topic = mgw_dc.com.gen_event_topic(device_id, service)
        else:
            response = {"command_id": command_id}
            if result is not None:
                response["data"] = json.dumps(result).replace("'", "\"")
            topic = mgw_dc.com.gen_response_topic(device_id, service)
        self.mqtt_client.publish(topic, json.dumps(response).replace("'", "\""), 2)
