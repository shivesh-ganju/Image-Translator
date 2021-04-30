from btpeer import *
from utils import *
import json


class TranslatorNode(BTPeer):
    def __init__(self, maxpeers, serverport, neighbourport, id, nid):
        BTPeer.__init__(self, maxpeers, serverport)
        self.region = "EU"
        self.requests = {}
        handlers = {
            "TRAN": self.translate,
            "ACKN": self.ack
        }
        for m_type in handlers.keys():
            self.addhandler(m_type, handlers[m_type])

        # self.addpeer(nid,'localhost',neighbourport)

    def translate(self, peer, data):
        print("I am translating")

    def ack(self, peer, data):
        print(data["message"])

    def main(self):
        # TODO: When creating a translation  request should also give user email.
        # Only user interface will ever create a translation request.
        data = create_translation_request_message(
            1, self.myid, "GR", self.myid, "Translate this sentence in french", "testmail@mail.com")
        data = json.dumps(data)
        self.connectandsend('52.207.203.252', 1234, "TRAN",
                            data, pid=self.myid, waitreply=False)


a = TranslatorNode(100, 4321, 4444, "A", "D")
a.main()
# import json
# a = {
#     "x":"y",
#     "a":"B"
# }
# x=json.dumps(a)
# print(json.loads(x)['x'])
