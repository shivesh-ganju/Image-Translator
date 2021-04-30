from btpeer import *
from utils import *
import os
import requests
import uuid
import json
from config import TRANSLATION_CONFIG
import random
from collections import deque


class BrokerNode(BTPeer):
    def __init__(self, maxpeers, serverport, name, register_server):
        BTPeer.__init__(self, maxpeers, serverport)
        self.region = "IT"
        self.requests = set()
        self.name = name
        self.register_server = register_server
        self.Q = deque()

        handlers = {
            "BINT": self.handle_interface_broker,
            "BTCR": self.handle_transcription_broker,
            "DISC": self.handle_discovery,
            "REGR": self.handle_register_reply,
            "DISR": self.handle_discovery_reply
        }
        for m_type in handlers.keys():
            self.addhandler(m_type, handlers[m_type])

    def handle_register_reply(self, peerconn, register_reply):
        print("I am ready to serve")
        register_reply = json.loads(register_reply)
        peerid, peeradd = register_reply["node_info"]
        if peerid == "unk":
            print("I am the first node in the P2P")
            return
        if register_reply["id"] in self.requests:
            return
        self.requests.add(register_reply["id"])
        peerhost, peerport = peeradd.split(":")
        # TOODO: not necessary to send self.myid twice.
        msg = create_message(self.myid, self.name, self.myid,
                             random.randint(0, 1000000), "DISC")
        self.connectandsend(peerhost, peerport, "DISC", json.dumps(
            msg), pid=self.myid, waitreply=False)

    def handle_discovery(self, peerconn, discovery_message):
        """
        peerconn: PeerConnection instance.
        discovery_message: message data json encoded. Need to get json dump of message before read.
        """
        discovery_message = json.loads(discovery_message)
        # peerid = nodeid in createMessage, or self.name.
        # peeradd = nodeinfo in create message, self.myid
        # self.myid = '%s:%d' % (self.serverhost, self.serverport).
        peerid, peeradd = discovery_message["node_info"]
        if discovery_message["id"] in self.requests:
            return
        self.requests.add(discovery_message["id"])
        for id in self.getpeerids():
            # Iterate though all peers and propogate discovery message of node.
            (host, port) = self.getpeer(id)
            self.connectandsend(host, port, "DISC", json.dumps(
                discovery_message), self.myid, waitreply=False)
        reply = create_message(self.myid, self.name,
                               self.myid, random.randint(0, 1000000), "DISR")
        self.addpeer(peerconn, peeradd.split(":")[0], peeradd.split(":")[1])
        self.connectandsend(peeradd.split(":")[0], peeradd.split(
            ":")[1], "DISR", json.dumps(reply), self.myid, waitreply=False)

    def handle_discovery_reply(self, peerconn, discovery_reply_message):
        discovery_message = json.loads(discovery_reply_message)
        peerid, peeradd = discovery_message["node_info"]
        if discovery_message["id"] in self.requests:
            return
        self.requests.add(discovery_message["id"])
        print("Added peer {}".format(peerid))
        self.addpeer(peerconn, peeradd.split(":")[0], peeradd.split(":")[1])

    def handle_interface_broker(self, peerconn, msg):
        pass

    def handle_transcription_broker(self, peerconn, msg):
        pass

    def update_IOT():
        """ 
        Will be called when a a broker node receives a message.
        Will send state if Q to AWS so can visualize using IOT. 
        """
        pass

    def handle_translate(self, peerconn, translation_request):
        translation_request = json.loads(translation_request)
        if translation_request["id"] in self.requests:
            return
        if self.region != translation_request["region"]:
            self.requests.add(translation_request["id"])
            for peerid in self.getpeerids():
                (host, port) = self.getpeer(peerid)
                self.connectandsend(host, port, "TRAN", json.dumps(
                    translation_request), pid=self.myid, waitreply=False)
            return
        self.requests.add(translation_request["id"])
        host, port, text = translation_request['requester'].split(
            ":")[0], translation_request['requester'].split(":")[1], translation_request['message']
        translated_text = self.translate(text)
        msg = create_translation_response_message(
            translation_request, self.myid, translated_text)
        cmp = json.dumps(msg)
        self.connectandsend(host, port, "ACKN", cmp,
                            pid=self.myid, waitreply=False)

    def translate(self, text):
        subscription_key = 'bfcfe92f1fa842e6a5cf95f622345b2c'
        endpoint = "https://api.cognitive.microsofttranslator.com/"
        path = '/translate?api-version=3.0'
        params = '&from=en&to=it'
        constructed_url = endpoint + path + params
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Ocp-Apim-Subscription-Region': 'eastus',
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        body = [{
            'text': text
        }]
        request = requests.post(constructed_url, headers=headers, json=body)
        response = request.json()
        print(response)
        return response[0]['translations'][0]['text']

    def handle_forward(self, peerconn, translation_request):
        msg = json.loads(translation_request)
        if msg["id"] in self.requests:
            return
        for peerid in self.getpeerids():
            self.requests.add(msg["id"])
            (host, port) = self.getpeer(peerid)
            self.connectandsend(host, port, msg["type"], json.dumps(
                translation_request), pid=self.myid, waitreply=False)

    def handle_translation_response(self, peerconn, translation_reponse):
        msg = json.loads(translation_reponse)
        print(msg["Message"])

    def register(self):
        host, port = self.register_server.split(":")
        msg = create_message(self.myid, self.name, self.myid,
                             random.randint(0, 100000), "REGS")
        cmp = json.dumps(msg)
        self.connectandsend(host, port, "REGS", cmp,
                            pid=self.myid, waitreply=False)

    def main(self):
        self.register()
        self.mainloop()


# TODO: What port should be used, currently chose a TCP, UDP compatible port.

node = BrokerNode(
    100, TRANSLATION_CONFIG["brkr"], "brkr", 'localhost:' + str(TRANSLATION_CONFIG["regr"]))
node.main()


"""
Flow:

1. We create instance and add all handler methods for the differnet message types.

2. We register node, by sending resgistartion message. We now address and port of registration server as provided in constructor. 

3. We call main loop and wait for messages. 


Questions:
Why do for every handler do we need to define a request and response handler?


"""
