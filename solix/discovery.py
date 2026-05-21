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

import asyncio
from typing import Dict

from mgw_dc.dm import device_state
from api import api
from api.mqtt_factory import SolixMqttDeviceFactory

from solix.command import Command
from util import get_logger, conf, diff, DCDevice
from util.router import Router

__all__ = ("Discovery",)

from util.device_manager import DeviceManager

logger = get_logger(__name__.split(".", 1)[-1])

device_types = {
    'A17C1': conf.Senergy.dt_A17C1,
    'A17X8': conf.Senergy.dt_A17X8,
}


class Discovery():
    def __init__(self, device_manager: DeviceManager, anker_solix_api: api.AnkerSolixApi, command: Command, router: Router):
        self._device_manager = device_manager
        self._anker_solix_api = anker_solix_api
        self._command = command
        self._router = router

    async def get_devices(self) -> Dict[str, DCDevice]:
        logger.info("Starting scan")
        devices: Dict[str, DCDevice] = {}
        await self._anker_solix_api.update_sites()
        await self._anker_solix_api.update_device_details()
        
        if (self._anker_solix_api.mqttsession is None or not self._anker_solix_api.mqttsession.is_connected()) and not (
            await self._anker_solix_api.startMqttSession(self.on_upstream_msg)
            and self._anker_solix_api.mqttsession.is_connected()
        ):
            logger.error("Could not start MQTT session with API")
            return {}
        
        devs = [
            dev
            for dev in self._anker_solix_api.devices.values()
            if dev.get("mqtt_supported")
        ]

        for dev in devs:
            # subscribe device
            topic = f"{self._anker_solix_api.mqttsession.get_topic_prefix(deviceDict=dev)}#"
            resp = self._anker_solix_api.mqttsession.subscribe(topic)
            if resp and resp.is_failure:
                logger.error(f"Failed subscription for topic: {topic}")

            try:
                mqttdevice = SolixMqttDeviceFactory(
                    api_instance=self._anker_solix_api, device_sn=dev['device_sn']).create_device()
                # DCDevice will manage its own periodic trigger
            except Exception as e:
                logger.error(
                    f"Could not initialize MQTT device for {dev['device_sn']}: {e}")
                continue
            pass
            
            
            logger.info("Discovered " + dev['alias'])
            logger.debug(f"Control details: {mqttdevice.controls}")
            if dev['device_pn'] not in device_types:
                logger.warning(
                    f"unrecognized device type {dev['device_pn']} will be skipped")
                continue
            dt = device_types[dev['device_pn']]
            id = conf.Discovery.device_id_prefix + dev['device_sn']
            attributes = [
                {"key": "solix/site_id", "value": dev['site_id']},
                {"key": "solix/device_pn", "value": dev['device_pn']},
            ]
            if 'generation' in dev:
                attributes.append(
                    {"key": "solix/generation", "value": f"{dev['generation']}"})
            if 'tag' in dev:
                attributes.append({"key": "solix/tag", "value": dev['tag']})
            devices[id] = DCDevice(id=id, name=dev['alias'], type=dt, state=device_state.online,
                                 mqttdevice=mqttdevice, solixdevice=dev, attributes=attributes)

        logger.info("Discovered " + str(len(devices)) + " devices")
        return devices

    def on_upstream_msg(self, _, topic, __, ___, ____, device_sn, payload):
        topicSegments = topic.split("/")
        self._router.tasks.put_nowait(
            (conf.Discovery.device_id_prefix + device_sn, topicSegments[-1], payload, True))

    async def _refresh_devices(self):
        try:
            devices = await self.get_devices()
            stored_devices = self._device_manager.get_devices()

            new_devices, missing_devices, existing_devices = diff(
                stored_devices, devices)
            if new_devices:
                for device_id in new_devices:
                    devices[device_id].start_periodic_trigger()
                    self._device_manager.handle_new_device(devices[device_id])
            if missing_devices:
                for device_id in missing_devices:
                    dev = stored_devices[device_id]
                    if hasattr(dev, "stop_periodic_trigger"):
                        dev.stop_periodic_trigger()
                    self._device_manager.handle_missing_device(dev)
            if existing_devices:
                for device_id in existing_devices:
                    self._device_manager.handle_existing_device(
                        stored_devices[device_id])
            self._device_manager.set_devices(devices=devices)
        except Exception as ex:
            logger.error("refreshing devices failed - {}".format(ex))

    async def discovery_loop(self):
        await self._refresh_devices()
        while True:
            await asyncio.sleep(conf.Discovery.scan_delay)
            await self._refresh_devices()
