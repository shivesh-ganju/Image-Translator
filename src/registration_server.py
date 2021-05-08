import os
import flask
app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "Registration Server"

# TODO: Should be interface node IP returned.


@app.route('/interface-node', methods=['GET'])
def get_broker_info():
    interface_nodes = []
    if os.path.exists('interface-info.txt'):
        file = open('interface-info.txt', 'rb')
        for line in file:
            print(line)
            interface_nodes.append(line.decode("utf-8").split('\n')[0])
        file.close()
    result = {"nodes": interface_nodes}
    return result


if __name__ == "__main__":
    app.run(debug=True, port=8080)
