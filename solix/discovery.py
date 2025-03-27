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

from util import get_logger, conf, diff, DCDevice

__all__ = ("Discovery",)

from util.device_manager import DeviceManager

logger = get_logger(__name__.split(".", 1)[-1])

device_types = {
    'solarbank': conf.Senergy.dt_solarbank,
    'smartplug': conf.Senergy.dt_plug,
}

class Discovery():
    def __init__(self, device_manager: DeviceManager, anker_solix_api: api.AnkerSolixApi):
        self._device_manager = device_manager
        self._anker_solix_api = anker_solix_api

    async def get_devices(self) -> Dict[str, DCDevice]:
        logger.info("Starting scan")
        devices: Dict[str, DCDevice] = {}
        await self._anker_solix_api.update_sites()
        await self._anker_solix_api.update_device_details()

        for _, dev in self._anker_solix_api.devices.items():
            logger.info("Discovered " + dev['alias'])
            if dev['type'] not in device_types:
                logger.warning(f"unrecognized device type {dev['type']} will be skipped")
                continue
            dt = device_types[dev['type']]
            id = conf.Discovery.device_id_prefix + dev['device_sn']
            attributes = [
                {"key": "solix/site_id", "value": dev['site_id']},
                {"key": "solix/device_pn", "value": dev['device_pn']},
            ]
            if 'generation' in dev:
                attributes.append({"key": "solix/generation", "value": f"{dev['generation']}"})
            if 'tag' in dev:
                attributes.append({"key": "solix/tag", "value": dev['tag']})
            devices[id] = DCDevice(id=id, name=dev['alias'], type=dt, state=device_state.online,
                                     device=dev, attributes=attributes)

        logger.info("Discovered " + str(len(devices)) + " devices")
        return devices

    async def _refresh_devices(self):
        try:
            devices = await self.get_devices()
            stored_devices = self._device_manager.get_devices()

            new_devices, missing_devices, existing_devices = diff(stored_devices, devices)
            if new_devices:
                for device_id in new_devices:
                    self._device_manager.handle_new_device(devices[device_id])
            if missing_devices:
                for device_id in missing_devices:
                    self._device_manager.handle_missing_device(stored_devices[device_id])
            if existing_devices:
                for device_id in existing_devices:
                    self._device_manager.handle_existing_device(stored_devices[device_id])
            self._device_manager.set_devices(devices=devices)
        except Exception as ex:
            logger.error("refreshing devices failed - {}".format(ex))

    async def discovery_loop(self):
        await self._refresh_devices()
        while True:
            await asyncio.sleep(conf.Discovery.scan_delay)
            await self._refresh_devices()
