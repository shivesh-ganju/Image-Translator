from btpeer import *
import json
class TranslatorNode(BTPeer):
    def __init__(self,maxpeers,serverport,neighbourport,id,nid):
        BTPeer.__init__(self,maxpeers,serverport)
        self.region = "FR"
        self.requests={}
        handlers={
            "TRAN":self.translate,
            "ACKN":self.ack
        }
        for type in handlers.keys():
            self.addhandler(type,handlers[type])

        self.addpeer(nid,'localhost',neighbourport)

    def translate(self,peerconn,data):
        text="I got the message"
        print("I got the message")
        msg={
            "id":self.myid,
            "msg":text,
            "port":self.serverport
        }
        data = json.loads(data)
        host,port=data['id'].split(":")[0],data['port']
        print(host)
        print(port)
        cmp = json.dumps(msg)
        self.connectandsend(host,4321,"ACKN",cmp,pid=self.myid,waitreply=False)
    def ack(self):
        print("I am acking")

    def main(self):
        self.mainloop()
node = TranslatorNode(100,1111,1212,"B","C")
node.main()