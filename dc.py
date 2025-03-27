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
import signal

from aiohttp import ClientSession
from api import api

from solix import Discovery, Command
from util import init_logger, conf, MQTTClient, handle_sigterm, Router, DeviceManager, Events
from util.logger import get_logger


logger = get_logger(__name__.split(".", 1)[-1])


async def main():
    async with ClientSession() as websession:
        mqtt_client = MQTTClient()
        device_manager = DeviceManager(mqtt_client=mqtt_client)
        anker_solix_api = api.AnkerSolixApi(
            conf.Solix.username,  conf.Solix.password,  conf.Solix.country, websession, logger
        )
        discovery = Discovery(device_manager=device_manager, anker_solix_api=anker_solix_api)
        command = Command(mqtt_client=mqtt_client, device_manager=device_manager, anker_solix_api=anker_solix_api)
        router = Router(refresh_callback=device_manager.publish_devices, command_callback=command.execute_command)
        mqtt_client.on_connect = device_manager.publish_devices
        mqtt_client.on_message = router.route
        events = Events(router=router, device_manager=device_manager, anker_solix_api=anker_solix_api)
        
        async with asyncio.TaskGroup() as tg:
            tg.create_task(discovery.discovery_loop())
            tg.create_task(router.run_tasks())
            tg.create_task(events.run())
            tg.create_task(mqtt_client.connect())

    

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)
    init_logger(conf.Logger.level)
    asyncio.run(main(), debug=False)
    

