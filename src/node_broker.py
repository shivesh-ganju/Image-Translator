from basepeer import *
from utils import *
import requests
import json
from config import TRANSLATION_CONFIG
import random
from collections import deque


class BrokerNode(BasePeer):
    def __init__(self, maxpeers, serverport, name, register_server):
        BasePeer.__init__(self, maxpeers, serverport, name, register_server)
        self.Q = deque()

        # Handlers defined for listining to messages.
        handlers = {
            "BINT": self.handle_interface_broker_request,
            "BTCR": self.handle_transcription_broker_request,
        }
        for m_type in handlers.keys():
            self.addhandler(m_type, handlers[m_type])

    def handle_interface_broker_request(self, peerconn, raw_msg):

        msg = json.loads(translation_request)
        if msg["id"] in self.requests:
            return

        self.requests.add(msg["id"])
        for peerid in self.getpeerids():
            (host, port) = self.getpeer(peerid)
            self.connectandsend(host, port, "TRSC", json.dumps(
                translation_request), pid=self.myid, waitreply=False)

    def handle_transcription_broker_request(self, peerconn, msg):
        pass

    def update_iot():
        """
        Will be called when a a broker node receives a message.
        Will send state if Q to AWS so can visualize using IOT.
        """
        pass

    # def handle_translate(self, peerconn, translation_request):
    #     translation_request = json.loads(translation_request)
    #     if translation_request["id"] in self.requests:
    #         return
    #     if self.region != translation_request["region"]:
    #         self.requests.add(translation_request["id"])
    #         for peerid in self.getpeerids():
    #             (host, port) = self.getpeer(peerid)
    #             self.connectandsend(host, port, "TRAN", json.dumps(
    #                 translation_request), pid=self.myid, waitreply=False)
    #         return
    #     self.requests.add(translation_request["id"])
    #     host, port, text = translation_request['requester'].split(
    #         ":")[0], translation_request['requester'].split(":")[1], translation_request['message']
    #     translated_text = self.translate(text)
    #     msg = create_translation_response_message(
    #         translation_request, self.myid, translated_text)
    #     cmp = json.dumps(msg)
    #     self.connectandsend(host, port, "ACKN", cmp,
    #                         pid=self.myid, waitreply=False)

    # def translate(self, text):
    #     subscription_key = 'bfcfe92f1fa842e6a5cf95f622345b2c'
    #     endpoint = "https://api.cognitive.microsofttranslator.com/"
    #     path = '/translate?api-version=3.0'
    #     params = '&from=en&to=it'
    #     constructed_url = endpoint + path + params
    #     headers = {
    #         'Ocp-Apim-Subscription-Key': subscription_key,
    #         'Ocp-Apim-Subscription-Region': 'eastus',
    #         'Content-type': 'application/json',
    #         'X-ClientTraceId': str(uuid.uuid4())
    #     }
    #     body = [{
    #         'text': text
    #     }]
    #     request = requests.post(constructed_url, headers=headers, json=body)
    #     response = request.json()
    #     print(response)
    #     return response[0]['translations'][0]['text']


node = BrokerNode(
    100, TRANSLATION_CONFIG["brkr"], "brkr", 'localhost:' + str(TRANSLATION_CONFIG["regr"]))
node.main()


"""
Flow:

1. We create instance and add all handler methods for the differnet message types.

2. We register node, by sending resgistartion message. We now address and port of registration server as provided in constructor.

3. Registered node sends a discovery message to the peer it received.

4. It now will wait for discovery replies from other peers. So it can addPeers().

5. Peer that has recived discovery message "DISC", propogates to all other peers. Not changing the content.
    Peer also responds with a "DISR" reply.

3. We call main loop and wait for messages.


"""
