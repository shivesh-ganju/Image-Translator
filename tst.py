from btpeer import *
import json
class TranslatorNode(BTPeer):
    def __init__(self,maxpeers,serverport,neighbourport,id,nid):
        BTPeer.__init__(self,maxpeers,serverport)
        self.region = "EU"
        self.requests={}
        handlers={
            "TRAN":self.translate,
            "ACKN":self.ack
        }
        for type in handlers.keys():
            self.addhandler(type,handlers[type])

        self.addpeer(nid,'localhost',neighbourport)

    def translate(self,peer,data):
        print("I am translating")

    def ack(self,peer,data):
        print("I am acking")

    def main(self):
        data={
            "id":self.myid,
            "port":self.serverport,
            "msg":"Translate"
        }
        data=json.dumps(data)
        self.connectandsend('localhost',1111,"TRAN",data,pid="B",waitreply=False)
        self.mainloop()

a = TranslatorNode(100,4321,4444,"A","D")
a.main()
# import json
# a = {
#     "x":"y",
#     "a":"B"
# }
# x=json.dumps(a)
# print(json.loads(x)['x'])