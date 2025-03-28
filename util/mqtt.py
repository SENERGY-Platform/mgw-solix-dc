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

__all__ = ("MQTTClient",)

import mgw_dc
from gmqtt import Client, Message

from .config import conf
from .logger import get_logger

logger = get_logger(__name__.split(".", 1)[-1])


class MQTTClient:
    def __init__(self):
        self.__client = Client(
            client_id=conf.Client.id,
            clean_session=conf.Client.clean_session,
            will_message=Message(mgw_dc.dm.gen_last_will_topic(conf.Client.id), "1", qos=2),
            logger=logger
        )
        self.__client.on_connect = self.__on_connect
        self.__client.on_disconnect = self.__on_disconnect
        self.__client.on_message = self.__on_message
        self.connected = self.__client.is_connected
        self.on_connect = None
        self.on_message = None

    def __on_connect(self, client, flags, rc, properties):
        if rc == 0:
            logger.info("connected to '{}'".format(conf.MsgBroker.host))
            self.__client.subscribe(mgw_dc.dm.gen_refresh_topic(), 1)
            self.on_connect()
        else:
            logger.error("could not connect to '{}'".format(conf.MsgBroker.host))

    def __on_disconnect(self, packet, exc=None):
        if exc == 0:
            logger.info("disconnected from '{}'".format(conf.MsgBroker.host))
        else:
            logger.warning("disconnected from '{}' unexpectedly".format(conf.MsgBroker.host))

    def __on_message(self, client, topic, payload, qos, properties):
        self.on_message(topic, payload)

    async def connect(self):
        await self.__client.connect(host=conf.MsgBroker.host, port=conf.MsgBroker.port, keepalive=conf.Client.keep_alive) 

    def subscribe(self, topic: str, qos: int) -> None:
        self.__client.subscribe(subscription_or_topic=topic, qos=qos)

    def unsubscribe(self, topic: str) -> None:
        self.__client.unsubscribe(topic=topic)

    def publish(self, topic: str, payload: str, qos: int) -> None:
        self.__client.publish(message_or_topic=topic, payload=payload, qos=qos, retain=False)