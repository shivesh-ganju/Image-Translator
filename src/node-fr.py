from btpeer import *
import os
import requests
import uuid
import json
from utils import *
from config import TRANSLATION_CONFIG
from threading import Thread
import random
import smtplib, ssl


class TranslatorNode(BTPeer):
    def __init__(self, maxpeers, serverport, name, register_server):
        BTPeer.__init__(self, maxpeers, serverport)
        self.region = "FR"
        self.requests = set()
        self.name = name
        self.register_server = register_server
        handlers = {
            "TRAN": self.handle_translate,
            "DISC": self.handle_discovery,
            "REGR": self.handle_register_reply,
            "DISR": self.handle_discovery_reply
        }
        self.registered=False
        for m_type in handlers.keys():
            self.addhandler(m_type, handlers[m_type])

    def handle_register_reply(self, peerconn, register_reply):
        self.registered=True
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
        peerid, peeradd = discovery_message["node_info"]
        if discovery_message["id"] in self.requests:
            return
        self.requests.add(discovery_message["id"])
        for id in self.getpeerids():
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
        if discovery_message["id"] in self.requests:
            return
        self.requests.add(discovery_message["id"])
        peerid, peeradd = discovery_message["node_info"]
        print("Added peer {}".format(peerid))
        self.addpeer(peerconn, peeradd.split(":")[0], peeradd.split(":")[1])

    def handle_forward(self, peerconn, translation_request):
        msg = json.loads(translation_request)
        if msg["id"] in self.requests:
            return

        self.requests.add(msg["id"])
        for peerid in self.getpeerids():
            (host, port) = self.getpeer(peerid)
            self.connectandsend(host, port, msg["type"], json.dumps(
                translation_request), pid=self.myid, waitreply=False)

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
        self.send_email(translated_text,translation_request["email"])

    def translate(self, text):
        subscription_key = 'bfcfe92f1fa842e6a5cf95f622345b2c'
        endpoint = "https://api.cognitive.microsofttranslator.com/"
        path = '/translate?api-version=3.0'
        params = '&from=en&to=fr'
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
        return response[0]['translations'][0]['text']

    def send_email(self, translated_text, email):
            # TODO: Should send email to user with the data.
            smtp_server = "smtp.gmail.com"
            port = 587  # For starttls
            sender_email = "imagetranslator214@gmail.com"
            password = "translateImage"
            receiver_email = email
            context = ssl.create_default_context()
            message = """\
    Subject: Request Ready

    Your translated text is : """ + translated_text
            # Try to log in to server and send email
            try:
                server = smtplib.SMTP(smtp_server, port)
                server.ehlo()  # Can be omitted
                server.starttls(context=context)  # Secure the connection
                server.ehlo()  # Can be omitted
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
            except Exception as e:
                # Print any error messages to stdout
                print(e)
            finally:
                server.quit()

    def register(self):
        import time
        while self.registered==False:
            host, port = self.register_server.split(":")
            msg = create_message(self.myid, self.name, self.myid,
                                 random.randint(0, 100000), "REGS")
            cmp = json.dumps(msg)
            self.connectandsend(host, port, "REGS", cmp,
                                pid=self.myid, waitreply=False)
            time.sleep(5)

    def main(self):
        reg_thread=Thread(target=self.register)
        reg_thread.start()
        self.mainloop()


node = TranslatorNode(
    100, TRANSLATION_CONFIG["fr"], "fr", 'localhost:'+str(TRANSLATION_CONFIG["regr"]))
node.main()
