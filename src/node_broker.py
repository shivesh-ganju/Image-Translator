from basepeer import *
from utils import *
import requests
import json
from config import TRANSLATION_CONFIG
import random
from datetime import datetime


class BrokerNode(BasePeer):
    def __init__(self, maxpeers, serverport, name, register_server):
        BasePeer.__init__(self, maxpeers, serverport, name, register_server)
        self.iot_gateway_url = "https://c02zu014q2.execute-api.eu-central-1.amazonaws.com/prod/message/"

        # Handlers defined for listining to messages.
        handlers = {
            "BINT": self.__handle_interface_broker_request,
            "BTCR": self.__handle_transcription_broker_request,
        }
        for m_type in handlers.keys():
            self.addhandler(m_type, handlers[m_type])

    def __handle_interface_broker_request(self, peerconn, translation_request):
        msg = json.loads(translation_request)
        if msg["id"] in self.requests:
            return

        self.requests.add(msg["id"])
        self.__update_iot("broker_interface", msg["id"])

        for peerid in self.getpeerids():
            (host, port) = self.getpeer(peerid)
            # Update message type, as going to transcription node.
            self.connectandsend(host, port, "TRSC", json.dumps(
                translation_request), pid=self.myid, waitreply=False)

    def __handle_transcription_broker_request(self, peerconn, translation_request):
        msg = json.loads(translation_request)
        if msg["id"] in self.requests:
            return

        self.requests.add(msg["id"])
        self.__update_iot("broker_transcriptor", msg["id"])

        for peerid in self.getpeerids():
            (host, port) = self.getpeer(peerid)
            # Update message type, as going to transcription node.
            self.connectandsend(host, port, "TRAN", json.dumps(
                translation_request), pid=self.myid, waitreply=False)

    def __update_iot(self, topic, newMessageId):
        """
        Will be called when a a broker node receives a message.
        Will publish message to differnet topics depending on if broker or transcription message.
        """
        constructed_url = self.iot_gateway_url + topic
        headers = {
            'Content-type': 'application/json',
        }
        body = [
            {
                "nodeid": self.myid,
                "queue": len(self.requests),
                "newMessageId": newMessageId,
                "datetime": datetime.today().strftime('%Y-%m-%d-%H:%M:%S'),
            }
        ]

        request = requests.post(constructed_url, headers=headers, json=body)
        response = request.json()
        print(response)


node = BrokerNode(
    100, TRANSLATION_CONFIG["brkr"], "brkr", 'localhost:' + str(TRANSLATION_CONFIG["regr"]))
node.main()


"""
Flow:

1. We create instance and add all handler methods for the differnet message types.

2. We register node, by sending resgistartion message. We now address and port of registration server as provided in constructor.

3. Registered node sends a discovery message to the peer it received.

4. It now will wait for discovery replies from other peers. So it can addPeers().

5. Peer that has received discovery message "DISC", propogates to all other peers. Not changing the content.
    Peer also responds with a "DISR" reply.

3. We call main loop and wait for messages.
"""
