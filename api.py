import json
import requests
from flask import Flask, request, render_template
import os
app = Flask(__name__)


class App:
    def __init__(self, blockchain=None, sig_to_ip_map=None, key =None, load=None):
        self.blockchain = blockchain
        self.sig_to_ip_map = sig_to_ip_map
        self.key = key
        self.__dict__ = json.loads(load) if load is not None else self.__dict__


    def __repr__(self):
        if self.__dict__ != json.loads(json.dumps(self.__dict__, indent=4)):
            print("error not representable")
        return json.dumps(self.__dict__, indent=4)

this_app = App()
this_app.blockchain = 1
this_app.sig_to_ip_map = 2
this_app.key = 3
print(this_app)
that_app = App(load = """{
    "blockchain": 5,
    "sig_to_ip_map": 4,
    "key": 4
}""")
print(that_app)


if os.path.isfile("current.app"):
    with open("current.app","r") as f:
        read = f.read()
        print(read)
        instance = App(load=read)
else:
    instance = App()
    instance.sig_to_ip_map = { "all":[]}
    print("no instance saved found, enter 0 if you want to create a new  block chain or 1 to import")
    if int(input("1/0:")) == 0:
        instance.blockchain = "new blockchain"
    else:
        instance.sig_to_ip_map= { "all":[input("input ip of some peer:")]}
        instance.blockchain = json.loads(requests.get('http://'+ instance.sig_to_ip_map["unknown"][0] +'/blockchain').text)

    st = input("Enter your SECP256k1 Signing Key in hex or else press enter:")#use walrus
    if len(st) == 64:
        instance.key = st
    else:
        instance.key = "9174e1d59d361ea7d7eececb044ee82d6dd90d9ffd37bfac95dd2ec88342c9d8" #import from ecc genrator
    with open("current.app","w") as f:
        f.write(repr(instance))

print(instance)

@app.route('/')
def hello_world():
    if request.remote_addr != "127.0.0.1":
        return 'Hello,'+request.remote_addr
    return render_template('manage.html', text=instance.__repr__().replace("\n","<br>\n"), appdict=instance.__dict__)


@app.route('/change_key')
def changekey():
    if request.remote_addr != "127.0.0.1":
        return 'Hello,'+request.remote_addr+" not allowed", 404
    if request.args.get('key') is None:
        return instance.key  + " is still current key remains unchanged"
    instance.key = request.args.get('key')
    return "changed key to " + instance.key

@app.route('/add_ip')
def add_ip():
    if request.remote_addr != "127.0.0.1":
        return 'Hello,'+request.remote_addr+" not allowed", 404
    if request.args.get('ip') is None:
        return "no ip was sent"
    instance.sig_to_ip_map["all"].append( request.args.get('ip'))
    return " addedd " + request.args.get('ip')

@app.route('/add_transaction')
def add_transaction():
    if request.args.get('transaction') is None:
        return "no transaction was sent"
    #"check if trasnaction is from self"
    # sign transaction
    #add to  mining block
    instance.blockchain += request.args.get('transaction')
    return " addedd " + request.args.get('transaction')


@app.route('/key')
def show_sign_key():
    return "6292c0e3af9ea9da8dc4a9232832871a1009ac0bf056c43b151fb17b02db36a39560499f949508db467da605049f80f3ec37702a47e5880e695b45b351fa865d"

@app.route('/ip_list')
def ip_list():
    return json.dumps(instance.sig_to_ip_map, indent=4)

@app.route('/blockchain')
def send_blockchain():
    return repr(instance.blockchain)

#app.run(host='0.0.0.0', port=8333, debug=True)
#app.run(host='localhost', port=8333)#, debug=True)
app.run(host='localhost', port=8333, debug=True)