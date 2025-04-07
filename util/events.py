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

__all__ = ("Events",)

import asyncio

import mgw_dc.com

from . import conf, Router, DeviceManager
from .logger import get_logger

from api import api

logger = get_logger(__name__.split(".", 1)[-1])

class Events():
    def __init__(self, router: Router, device_manager: DeviceManager, anker_solix_api: api.AnkerSolixApi):
        self.router = router
        self.device_manager = device_manager
        self._anker_solix_api = anker_solix_api

    async def queue_status(self):
        while True:
            await self._anker_solix_api.update_sites()
            await self._anker_solix_api.update_site_details()
            await self._anker_solix_api.update_device_details()
            await self._anker_solix_api.update_device_energy()
            for device in self.device_manager.get_devices().values():
                self.router.route(mgw_dc.com.gen_command_topic(device.id, conf.Senergy.service_status), "", True)
            await asyncio.sleep(conf.Senergy.events_status_seconds)

    async def run(self) -> None:
        logger.info("Scheduling events....")
        
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.queue_status())