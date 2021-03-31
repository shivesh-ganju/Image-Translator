from btpeer import *

class TranslatorNode(BTPeer):
    def __init__(self,maxpeers,serverport,neighbourport,id,nid):
        BTPeer.__init__(self,maxpeers,serverport,myid=id)
        self.region = "GR"
        self.requests={}
        handlers={
            "TRAN":self.translate,
            "ACKN":self.ack
        }
        for type in handlers.keys():
            self.addhandler(type,handlers[type])

        self.addpeer(nid,'localhost',neighbourport)

    def translate(self,peer,key):
        print("I am translating")

    def ack(self):
        print("I am acking")

    def main(self):
        self.mainloop()
node = TranslatorNode(100,1212,2121,"C","D")
node.main()



