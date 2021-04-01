# Image-Translator
Steps to run this on EC2
1) Launch an Ec2 instance in the same region us-east-1
2) Configre the security group of the EC2, add rules under Inbound like this
2.1) All TCP  0-65535 0.0.0.0
2.2) All UDP  0-65535 0.0.0.0
3.) Assign an Elastic IP for your EC2. Available in the left tab on the EC2 Dashboard
4.) do ssh-keygen on ec2-server and ping me the ssh keys.
5.) perform a git clone on server
