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
        enable_mqtt = False

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
        dt_solarbank = "urn:infai:ses:device-type:85d88662-340d-4f18-a3a2-9d62d6fd62b5"
        dt_plug = "urn:infai:ses:device-type:7527dff5-59bf-43a0-9423-bc07b7d2c135"
        service_status = "status"
        events_status_seconds = 30
        
    @simple_env_var.section
    class Solix:
        username = ""
        password = ""
        country = "DE"

conf = Conf()

