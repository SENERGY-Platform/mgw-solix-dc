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

__all__ = ("conf",)

import simple_env_var


@simple_env_var.configuration
class Conf:
    @simple_env_var.section
    class MsgBroker:
        host = "message-broker"
        port = 1881

    @simple_env_var.section
    class Logger:
        level = "info"

    @simple_env_var.section
    class Client:
        clean_session = False
        keep_alive = 30
        id = "mgw-solix"
        
    @simple_env_var.section
    class Discovery:
        device_id_prefix = "solix-"
        scan_delay = 86400 # 1 day

    @simple_env_var.section
    class Senergy:
        dt_A17C1 = "urn:infai:ses:device-type:50d13003-3e44-4e32-92c4-925291842f3d"
        dt_A17X8 = "urn:infai:ses:device-type:75b63906-dab5-494c-8ad1-712ae9f66068"
        
    @simple_env_var.section
    class Solix:
        username = ""
        password = ""
        country = "DE"

conf = Conf()

