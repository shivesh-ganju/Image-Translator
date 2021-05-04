from basepeer import BasePeer
import requests
import json
from config import TRANSLATION_CONFIG
from utils import create_translation_request_message
# import random


class InterfaceNode(BasePeer):
    """
    Needs to handle following incoming requests:
    * Client connection, should deliver HTML. Maybe do over CLI?

    Outgoing response:
    * Needs to let client know if request has been submitted. 

    Outgoing request:
    * Needs to create initial transaltion message and send to a broker node.
    """

    def __init__(self, maxpeers, serverport, name, register_server):
        BasePeer.__init__(self, maxpeers, serverport, name, register_server)

    # def __handle_interface_broker_request(self, peerconn, translation_request):
    #     msg = json.loads(translation_request)
    #     if msg["id"] in self.requests:
    #         return

    #     self.requests.add(msg["id"])

    #     for peerid in self.getpeerids():
    #         (host, port) = self.getpeer(peerid)
    #         # Update message type, as going to transcription node.
    #         self.connectandsend(host, port, "TRSC", json.dumps(
    #             translation_request), pid=self.myid, waitreply=False)


node = InterfaceNode(
    100, TRANSLATION_CONFIG["interface"], "interface", 'localhost:' + str(TRANSLATION_CONFIG["regr"]))
node.main()


"""
How can you server HTML and JS using only a TCP/IP server?






"""
