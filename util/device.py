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

import typing

import mgw_dc.dm

from api.mqtt_device import SolixMqttDevice
from util import get_logger

__all__ = ("DCDevice",)

logger = get_logger(__name__.split(".", 1)[-1])


class DCDevice(mgw_dc.dm.Device):
    def __init__(self, id: str, name: str, type: str, mqttdevice: SolixMqttDevice, solixdevice: dict, state: typing.Optional[str] = None,
                 attributes=None):
        super().__init__(id, name, type, state, attributes)
        self._mqttdevice = mqttdevice
        self._solixdevice = solixdevice
        self._periodic_trigger_task: typing.Optional[typing.Any] = None

    def get_mqtt_device(self) -> SolixMqttDevice:
        return self._mqttdevice
    
    def get_solix_device(self) -> dict:
        return self._solixdevice

    def start_periodic_trigger(self):
        interval: int = 600
        import asyncio
        if self._periodic_trigger_task is not None and not self._periodic_trigger_task.done():
            return

        async def periodic():
            try:
                while True:
                    try:
                        logger.debug(f"Triggering realtime update for device {self._mqttdevice.sn}")
                        await self._mqttdevice.realtime_trigger(timeout=interval)
                    except Exception as ex:
                        logger.error(
                            f"Error occurred while triggering realtime update for device {self._mqttdevice.device_sn}: {ex}")
                    await asyncio.sleep(interval)
            except asyncio.CancelledError:
                logger.info(
                    f"Periodic trigger cancelled for device {self._mqttdevice.device_sn}")
                return

        self._periodic_trigger_task = asyncio.create_task(periodic())

    def stop_periodic_trigger(self):
        if self._periodic_trigger_task is not None and not self._periodic_trigger_task.done():
            self._periodic_trigger_task.cancel()
        self._periodic_trigger_task = None
