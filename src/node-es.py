from btpeer import *
from utils import *
import os
import requests
import uuid
import json
from config import TRANSLATION_CONFIG
import random


class TranslatorNode(BTPeer):
    def __init__(self, maxpeers, serverport, name, register_server):
        BTPeer.__init__(self, maxpeers, serverport)
        self.region = "ES"
        self.name = name
        self.register_server = register_server
        self.requests = set()
        handlers = {
            "TRAN": self.handle_translate,
            "ACKT": self.handle_translation_response,
            "DISC": self.handle_discovery,
            "REGR": self.handle_register_reply,
            "DISR": self.handle_discovery_reply
        }
        for h_type in handlers.keys():
            self.addhandler(h_type, handlers[h_type])

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
        msg = create_message(self.myid, self.name, self.myid,
                             random.randint(0, 1000000), "DISC")
        self.connectandsend(peerhost, peerport, "DISC", json.dumps(
            msg), pid=self.myid, waitreply=False)

    def handle_discovery(self, peerconn, discovery_message):
        discovery_message = json.loads(discovery_message)
        if discovery_message["id"] in self.requests:
            return
        self.requests.add(discovery_message["id"])
        peerid, peeradd = discovery_message["node_info"]
        for id in self.getpeerids():
            (host, port) = self.getpeer(id)
            self.connectandsend(host, port, "DISC", json.dumps(
                discovery_message), self.myid, waitreply=False)
        reply = create_message(self.myid, self.name,
                               self.myid, random.randint(0, 1000000), "DISR")
        self.addpeer(peerid, peeradd.split(":")[0], peeradd.split(":")[1])
        self.connectandsend(peeradd.split(":")[0], peeradd.split(
            ":")[1], "DISR", json.dumps(reply), self.myid, waitreply=False)

    def handle_discovery_reply(self, peerconn, discovery_reply_message):
        discovery_message = json.loads(discovery_reply_message)
        if discovery_message["id"] in self.requests:
            return
        self.requests.add(discovery_message["id"])
        peerid, peeradd = discovery_message["node_info"]
        print("Added peer {}".format(peerid))
        self.addpeer(peerid, peeradd.split(":")[0], peeradd.split(":")[1])

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
        self.connectandsend(host, port, "ACKT", cmp,
                            pid=self.myid, waitreply=False)

    def translate(self, text):
        subscription_key = 'bfcfe92f1fa842e6a5cf95f622345b2c'
        endpoint = "https://api.cognitive.microsofttranslator.com/"
        path = '/translate?api-version=3.0'
        params = '&from=en&to=es'
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


node = TranslatorNode(
    100, TRANSLATION_CONFIG["es"], "es", 'localhost:'+str(TRANSLATION_CONFIG["regr"]))
node.main()
