"""
   Copyright 2026 InfAI (CC SES)

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


from api import api

from util import DCDevice


async def handle_sb2_home_load(device: DCDevice, anker_solix_api: api.AnkerSolixApi, payload: typing.Dict, service: str, *args, **kwargs) -> typing.Union[typing.Dict, typing.Optional[str]]:
    dev = device.get_solix_device()
    result = await anker_solix_api.set_sb2_home_load(dev['site_id'], dev['device_sn'], **payload)
    return result, None
