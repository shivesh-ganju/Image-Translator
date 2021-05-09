# Image-Translator

## How to run using EC2 VMs

1. Launch an EC2 instance in the same region us-east-1

2. Configure the security group of the EC2, add rules under Inbound like this
   2.1) All TCP 0-65535 0.0.0.0
   2.2) All UDP 0-65535 0.0.0.0
   3.) Assign an Elastic IP for your EC2. Available in the left tab on the EC2 Dashboard
   4.) Do ssh-keygen on ec2-server and ping me the ssh keys.

3. Run program as followed
   a) Run `git clone https://github.com/shivesh-ganju/Image-Translator.git`
   b) Install dependencies by running `pip install -r requirements.txt`
   c) Run the corresponding node `.py` files.

   e.g.

   - Registration node `python3 src/node_register_server`.
   - Translation node `python3 src/node_it.py`.
   - Broker node `python3 src/node_broker.py`
   - Interface node `python3 src/node_interface.py`

## Interface node additional required steps to run

If you want to run an `interface node` you also have to install the following repo:

```
git clone https://github.com/trozler/interface_nodes_btpeer.git
cd interface_nodes_btpeer
npm i
npm run build
node app.js
```

For more information on the web server, which uses Ethereum for payments, please refer to [trozler/interface_nodes_btpeer](https://github.com/trozler/interface_nodes_btpeer.git).

## IoT Api gateway

This project makes use of an IoT API gateway. The gateway is used to captured the state of the broker nodes.

The repo containing the code used to deploy the IoT gateway can be found at [trozler/image_translator_iotgateway](https://github.com/trozler/image_translator_iotgateway).
