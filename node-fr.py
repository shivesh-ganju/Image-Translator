from btpeer import *
import os, requests, uuid, json
from utils import *

class TranslatorNode(BTPeer):
    def __init__(self,maxpeers,serverport,neighbourport,id,nid):
        BTPeer.__init__(self,maxpeers,serverport)
        self.region = "FR"
        self.requests={}
        handlers={
            "TRAN":self.handle_translate,
            "ACKN":self.ack
        }
        for type in handlers.keys():
            self.addhandler(type,handlers[type])

        self.addpeer(nid,'107.20.33.48',neighbourport)
        #self.addpeer(nid, 'localhost', neighbourport)

    def handle_translate(self,peerconn,translation_request):
        translation_request = json.loads(translation_request)
        if self.region != translation_request["region"]:
            for peerid in self.getpeerids():
                (host,port) = self.getpeer(peerid)
                self.connectandsend(host,port,"TRAN",json.dumps(translation_request),pid=self.myid,waitreply=False)
            return
        host,port,text=translation_request['requester'].split(":")[0],translation_request['requester'].split(":")[1],translation_request['message']
        translated_text = self.translate(text)
        msg = create_translation_response_message(translation_request,self.myid,translated_text)
        cmp = json.dumps(msg)
        self.connectandsend(host,port,"ACKN",cmp,pid=self.myid,waitreply=False)

    def translate(self,text):
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

    def ack(self,peerconn,data):
        data = json.loads(data)
        print(data["msg"])

    def main(self):
        self.mainloop()
node = TranslatorNode(100,1111,1234,"B","A")
node.main()