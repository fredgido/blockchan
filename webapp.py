import hashlib
import json
import time
import os
import random
random.seed(0)
import ecdsa
from hashlib import sha3_512
import requests
import threading
import click

from flask import Flask, request, render_template
app = Flask(__name__)


class JCoder(json.JSONEncoder): #json.dumps(obj, default=lambda o: o.__dict__)
    def default(self, obj):
        if type(obj).__name__ == "Thread":
            return "Thread "+ ("running" if obj.is_alive() else "stopped")
        try:
            return obj.__dict__
        except:
            return repr(obj)


class App:
    def __init__(self, blockchain=None, sig_to_ip_map=None, key=None, load=None, loadfile=None,pending_trans=None):
        if loadfile is not None:
            self.boot(loadfile)
            return
        self.blockchain = blockchain if blockchain is not None else BlockChain()
        self.sig_to_ip_map = sig_to_ip_map if sig_to_ip_map is not None else {"all": []}
        self.key = self.load_key() if key is None else key
        self.pending_trans = pending_trans if pending_trans is not None else {"processing_thread": None, "pending_list":[],"run_signal":[True]}
        self.__dict__ = json.loads(load) if load is not None else self.__dict__
        #self.__thread = None

    def load_key(self, file="key.sk"):
        if os.path.isfile(file):
            with open(file, "rb") as f:
                return f.read().hex()                # sk = ecdsa.SigningKey.from_string(read, curve=ecdsa.SECP256k1, hashfunc=sha3_512)
        else:
            with open(file, "wb") as f:
                f.write(ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512).to_string())

    def save(self, appfile="current.app"):
        with open(appfile, "w") as f:
            f.write(repr(self))

    def boot(self,appfile="current.app"):
        if os.path.isfile(appfile):
            with open(appfile, "r") as f:
                #read = f.read()
                #print(read)
                self.__dict__ = json.loads(f.read())
        else:
            print("no instance saved found, enter 0 if you want to create a new  block chain or 1 to import")
            if int(input("1/0:")) == 0:
                self.blockchain = "new blockchain"
            else:
                self.sig_to_ip_map = {"all": [input("input ip of some peer:")]}
                self.blockchain = json.loads(requests.get('http://' + self.sig_to_ip_map["unknown"][0] + '/blockchain').text)

            st = input("Enter your SECP256k1 Signing Key in hex or else press enter:")  # use walrus
            if len(st) == 64:
                self.key = st
            else:
                self.key = "9174e1d59d361ea7d7eececb044ee82d6dd90d9ffd37bfac95dd2ec88342c9d8"  # import from ecc genrator
            self.save(appfile)

    def add_transaction(self,trans):
        self.pending_trans["pending_list"].append(trans)
        if self.pending_trans["processing_thread"] is not None:
            if self.pending_trans["processing_thread"].is_alive():
                print("miner is running")
                return
            print("stopping miner")
            self.pending_trans["run_signal"][0] = False
            self.pending_trans["processing_thread"].join()
            print(self.pending_trans["processing_thread"].is_alive())
        if hasattr(self.blockchain.chain[-1], 'status'):
            self.blockchain.chain.pop()
        current_block = Block(data=self.pending_trans["pending_list"], previous_hash=self.blockchain.chain[-1].hash)
        current_block.status = "being mined"
        self.blockchain.chain.append(current_block)
        self.pending_trans["run_signal"][0] = True
        t1 = threading.Thread(target=current_block.minenonce, kwargs={'miner': self.ver_key, 'run_signal': self.pending_trans["run_signal"]})
        t1.mined_block = current_block
        t2 = threading.Thread(target=self.wait_for_mine_complete, kwargs={'thread': t1})
        t1.start()
        t2.start()
        self.pending_trans["processing_thread"] = t1;

    def wait_for_mine_complete(self,thread):
        thread.join()
        if self.blockchain.chain[-2].hash == self.blockchain.chain[-1].previous_hash and self.blockchain.chain[-1].hash[0:3] == ("0" * 3):
            print("HELLO WORLD HERE IS SUCESS MINE")
            self.blockchain.chain[-1].data = json.loads(json.dumps(self.blockchain.chain[-1].data))
            for trans_comp in self.blockchain.chain[-1].data:
                for trans in self.pending_trans["pending_list"]:
                    if json.dumps(trans_comp, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True) == json.dumps(trans, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True):
                        self.pending_trans["pending_list"].remove(trans)

    def receive_block(self,block):
        print("recived block with prevhash " + str(block.previous_hash))
        for num,old_block in enumerate(self.blockchain.chain):
            print( "comapring "+ str(old_block._hash))
            if block.previous_hash == old_block._hash:
                print("this block belongs in " + str(num+1))
                if self.blockchain.chain[num+1].validhash:
                    print("but we already have valid")
                else:
                    print("ok but we have invalid there block number "+str(num+1)+" of "+str(len(self.blockchain.chain)))
                    self.blockchain.chain[num+1] = block
                    for trans_comp in block.data:
                        for trans in self.pending_trans["pending_list"]:
                            if json.dumps(trans_comp, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True) == json.dumps(trans, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True):
                                self.pending_trans["pending_list"].remove(trans)


    @property
    def ver_key(self):
        return ecdsa.SigningKey.from_string(bytes.fromhex(self.key), curve=ecdsa.SECP256k1, hashfunc=sha3_512).verifying_key.to_string().hex()

    def __repr__(self):
        return json.dumps(self, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True)


class Transaction:
    def __init__(self, data, sign=None, signer=None,sign_key=None):
        self.data = data
        self.sign = sign
        self.signer = signer
        self._hash = self.hash
        if sign_key is not None:
            self.signit(sign_key)

    def signit(self, sk):
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(sk), curve=ecdsa.SECP256k1, hashfunc=sha3_512)
        self.sign = sk.sign(json.dumps(self.data, sort_keys=True, ensure_ascii=True, cls=JCoder).encode('ascii')).hex()
        self.signer = sk.verifying_key.to_string().hex()
        return True

    def verify(self):
        try:
            vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(self.signer), curve=ecdsa.SECP256k1, hashfunc=sha3_512)
            return vk.verify(bytes.fromhex(self.sign), json.dumps(self.data, sort_keys=True, ensure_ascii=True).encode('ascii'))
        except:
            return False

    @property
    def hash(self):
        self._hash = hashlib.sha3_512(json.dumps(self.data, sort_keys=True, ensure_ascii=True).encode('ascii')).hexdigest()
        return self._hash

    def __repr__(self):
        return json.dumps(self, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True)


class Block:
    def __init__(self, data, previous_hash=int(0).to_bytes(64, 'big').hex(), nonce=0, miner=("0" * 128), timestamp=None):
        self.previous_hash = previous_hash
        self.data = data
        self.miner = miner
        self.timestamp = timestamp if timestamp is not None else int(time.time())
        self.nonce = nonce
        self._hash = self.hash

    def minenonce(self, diff=3, miner=None,run_signal=(True, )):
        self.miner = miner if miner is not None else self.miner
        self.nonce = random.randint(0, 2 ** 30) if self.nonce == 0 else self.nonce
        while self.hash[0:diff] != ("0" * diff) and run_signal[0]:
            self.nonce += 1
            self.timestamp = int(time.time())
            # print(self.hash[0:diff]+"\n"+str(self.nonce)+"\n")
            #time.sleep(1)
        if(run_signal[0] == False):
            print("exit signal")
            self.status = "stopped mining"
            return self
        if hasattr(self, 'status'):
            delattr(self, 'status')
        return self

    @property
    def hash(self):
        self._hash = hashlib.sha3_512((self.previous_hash + repr(self.data) + self.miner).encode('ascii')+ self.timestamp.to_bytes(32,'big')+ self.nonce.to_bytes(32,'big')).hexdigest()
        return self._hash

    @property
    def validhash(self,diff=3):
        return self.hash[0:diff] == ("0" * diff)

    def __repr__(self):
        return json.dumps(self, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True)


class BlockChain:
    def __init__(self, jsonrepr=None):
        if isinstance(jsonrepr, str):
            vars(self).update(dict)
        else:
            self.chain = [self.boot()]

    def parse(self, jsonrepr):
        return json.loads(jsonrepr)

    def boot(self):
        return Block(data="start").minenonce(miner=("0" * 128))

    def addblock(self, newblock: Block,ver_key=None):
        print(self.chain[-1].hash)
        newblock.previous_hash = self.chain[-1].hash
        self.chain.append(newblock.minenonce(miner=ver_key))

    def validate(self):
        for i in range(1, len(self.chain)):
            if self.chain[i].previous_hash != self.chain[i - 1].hash:
                print("invalid hash on " + str(i) + "\n" + self.chain[i].previous_hash + "\n" + self.chain[i - 1].hash)
                return False
        return True

    def __repr__(self):
        return json.dumps(self, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True)


#this_app = App(loadfile="current.app")
#print(this_app)
this_app = App()
print(this_app)
a = Transaction({"moviments": {"Fred": 10, "John": 20}, "time": int(time.time())},sign_key=this_app.key)
this_app.blockchain.addblock(Block(data=a),ver_key=this_app.ver_key)
print(this_app)
this_app.add_transaction(trans=["test"])
#this_app.pending_trans["pending_list"].append(["data2"])
#print(this_app)
this_app.pending_trans["run_signal"][0] = False
#print(this_app)
this_app.pending_trans["processing_thread"].join()
print(this_app)
inc_block = Block(data=["test"],previous_hash=this_app.blockchain.chain[-1].previous_hash).minenonce()
print("printing incoming block")
print(inc_block)
print(this_app)
this_app.receive_block(inc_block)
print("printing app after recieving")
print(this_app)

print(this_app.pending_trans["processing_thread"].mined_block)



@app.route('/')
def hello_world():
    #if request.remote_addr != "127.0.0.1":
     #   return 'Hello,'+request.remote_addr
    return render_template('manage.html', text=this_app.__repr__(), appdict=this_app.__dict__) #.replace("\n","<br>\n")


@app.route('/change_key')
def changekey():
    if request.remote_addr != "127.0.0.1":
        return 'Hello,'+request.remote_addr+" not allowed", 404
    if request.args.get('key') is None:
        return this_app.key  + " is still current key remains unchanged"
    this_app.key = request.args.get('key')
    return "changed key to " + this_app.key

@app.route('/add_ip')
def add_ip():
    if request.remote_addr != "127.0.0.1":
        return 'Hello,'+request.remote_addr+" not allowed", 404
    if request.args.get('ip') is None:
        return "no ip was sent"
    this_app.sig_to_ip_map["all"].append( request.args.get('ip'))
    return " addedd " + request.args.get('ip')

@app.route('/add_transaction')
def add_transaction():
    if request.args.get('transaction') is None:
        return "no transaction was sent"
    #"check if trasnaction is from self"
    # sign transaction
    #add to  mining block
    this_app.add_transaction( request.args.get('transaction'))
    return " addedd " + request.args.get('transaction')


@app.route('/blockchain')
def send_blockchain():
    return repr(this_app.blockchain)

@app.route('/key')
def show_sign_key():
    return this_app.ver_key

@app.route('/ip_list')
def ip_list():
    return json.dumps(this_app.sig_to_ip_map, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True)

@app.route('/receive_mined_block')
def receive_mined_block():
    if request.args.get('block') is None:
        return "no block was sent"
    # "check if trasnaction is from self"
    # sign transaction
    # add to  mining block
    block = Block()
    try:
        block.__dict__ = json.loads(request.args.get('block'))
    except:
        return "error parsing"
    this_app.receive_block(block)
    return " addedd " + json.dumps(block, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True)

#app.run(host='0.0.0.0', port=8333, debug=True)
#app.run(host='localhost', port=8333)#, debug=True)
app.run(host='0.0.0.0', port=8333, debug=True)



