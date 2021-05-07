import os
import flask
app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "Registration Server"

@app.route('/broker-node',methods=['GET'])
def get_broker_info():
    broker_nodes=[]
    if os.path.exists('broker-info.txt'):
        file = open('broker-info.txt','rb')
        for line in file:
            print(line)
            broker_nodes.append(line.decode("utf-8").split('\n')[0])
        file.close()
    result={"nodes":broker_nodes}
    return result

if __name__ == "__main__":
    app.run(debug=True,port=8080)