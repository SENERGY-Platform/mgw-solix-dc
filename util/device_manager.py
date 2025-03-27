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
from typing import Dict

import mgw_dc
from mgw_dc.dm import device_state

from util import MQTTClient, DCDevice, get_logger, conf

__all__ = ("DeviceManager",)
logger = get_logger(__name__.split(".", 1)[-1])


class DeviceManager():
    def __init__(self, mqtt_client: MQTTClient):
        self._mqtt_client = mqtt_client
        self._devices: Dict[str, DCDevice] = {}

    def is_device_id_known(self, device_id: str):
        return device_id in self._devices

    def handle_new_device(self, device: DCDevice):
        try:
            logger.info("adding '{}'".format(device.id))
            self._mqtt_client.subscribe(topic=mgw_dc.com.gen_command_topic(device.id), qos=1)
            self._mqtt_client.publish(
                topic=mgw_dc.dm.gen_device_topic(conf.Client.id),
                payload=json.dumps(mgw_dc.dm.gen_set_device_msg(device)),
                qos=1
            )
        except Exception as ex:
            logger.error("adding '{}' failed - {}".format(device.id, ex))

    def handle_missing_device(self, device: DCDevice):
        device.state = device_state.offline
        try:
            logger.info("setting '{}' offline ...".format(device.id))
            self._mqtt_client.publish(
                topic=mgw_dc.dm.gen_device_topic(conf.Client.id),
                payload=json.dumps(mgw_dc.dm.gen_set_device_msg(device)),
                qos=1
            )
            self._mqtt_client.unsubscribe(topic=mgw_dc.com.gen_command_topic(device.id))
        except Exception as ex:
            logger.error("removing '{}' failed - {}".format(device.id, ex))

    def handle_existing_device(self, device: DCDevice):
        try:
            logger.info("updating '{}' ...".format(device.id))
            self._mqtt_client.publish(
                topic=mgw_dc.dm.gen_device_topic(conf.Client.id),
                payload=json.dumps(mgw_dc.dm.gen_set_device_msg(device)),
                qos=1
            )
        except Exception as ex:
            logger.error("updating '{}' failed - {}".format(device.id, ex))

    def publish_devices(self):
        for _, device in self._devices.items():
            try:
                self._mqtt_client.publish(
                    topic=mgw_dc.dm.gen_device_topic(conf.Client.id),
                    payload=json.dumps(mgw_dc.dm.gen_set_device_msg(device)),
                    qos=1
                )
            except Exception as ex:
                logger.error("setting device '{}' failed - {}".format(device.id, ex))

    def get_devices(self) -> Dict[str, DCDevice]:
        return self._devices

    def set_devices(self, devices: Dict[str, DCDevice]):
        self._devices = devices
