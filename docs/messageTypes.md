## P2P node types and message types

The service is built in a peer to peer architecture, where each node within the network provides a specific service. In total we have 4 different node types:

**Interface node**
Will be the node the user interacts with and uploads their (picture, email) and pays using meta mask.
Publishes “transcription” tasks to broker nodes.

**Broker node**
Will publish messages from Interface and Transcription nodes.
Will send messages to subscribed Transcription and Translation nodes.

Example flow:

1. If an Interface node publishes a message, the broker will add the message to the queue and send it to a Transcription node

   - Receiving message type will be _“BINT”_ in BTPeer.
   - Send a message out using _"TRSC"_.

2. If a Transcription node publishes a message, the broker will add it to the queue and send it to a Translation node.

   - Receiving message type will be _“BTCR”_ in BTPeer.
   - Send a message out using _"TRAN"_.

3. If a broker node wants to leave the network the queue needs to be propagated to another broker node.
   - Everytime the state of the broker queue changes it will call an API provided by AWS API gateway. This API will be used to visualize the message flow and satisfy the IoT requirement.

**Transcription node**

1. All Transcription nodes will subscribe to messages from all broker nodes.
   - Receiving message type from broker node is _TRSC_.

**Translation node**

1. All Translation nodes will subscribe to messages from all broker nodes.
   - Will also send email to users containing final results.
   - Receiving message type from broker node is _“TRAN”_.
