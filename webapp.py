import hashlib
import json
import time
import os
import random
import ecdsa
import copy
from hashlib import sha3_512
import requests
import threading
import argparse
from contextlib import suppress
from flask import Flask, request, render_template
import jsonpickle


random.seed(0)

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, choices=range(0, 65535), required=False, default=8333)
args = parser.parse_args()
print(args)
print(args.port)

app = Flask(__name__)


class JCoder(json.JSONEncoder):  # json.dumps(obj, default=lambda o: o.__dict__)
    def default(self, obj):
        if type(obj).__name__ == "Thread":
            return "Thread " + ("running" if obj.is_alive() else "stopped")
        try:
            return obj.__dict__
        except:
            return repr(obj)


class App:
    def __init__(self, blockchain=None, sig_to_ip_map=None, key=None, load=None, loadfile=None, pending_trans=None):
        if loadfile is not None:
            self.boot(loadfile)
            return
        self.blockchain = blockchain if blockchain is not None else BlockChain()
        self.sig_to_ip_map = sig_to_ip_map if sig_to_ip_map is not None else {"all": []}
        self.key = self.load_key() if key is None else key
        self.pending_trans = pending_trans if pending_trans is not None else {"processing_thread": None, "pending_list": [], "run_signal": [True]}
        self.pending_block = Block(data=self.pending_trans["pending_list"],miner=self.ver_key)
        self.pending_block.status="booted"
        self.__dict__ = json.loads(load) if load is not None else self.__dict__

    def load_key(self, file="key.sk"):
        if not os.path.isfile(file):
            with open(file, "wb") as f:
                f.write(ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512).to_string())
        with open(file, "rb") as f:
            self.key = f.read().hex()
            return self.key  # sk = ecdsa.SigningKey.from_string(read, curve=ecdsa.SECP256k1, hashfunc=sha3_512)

    def save(self, appfile="current.app"):
        with open(appfile, "w") as f:
            f.write(repr(self))

    def boot(self, appfile="current.app"):
        if os.path.isfile(appfile):
            with open(appfile, "r") as f:               # read = f.read()                # print(read)     not yetworking
                self.__dict__ = jsonpickle.loads(f.read())
        else: #deprecate?
            print("no instance saved found, enter 0 if you want to create a new  block chain or 1 to import")
            if int(input("1/0:")) == 0:
                self.blockchain = BlockChain()
            else:
                self.sig_to_ip_map = {"all": [input("input ip of some peer:")]}
                self.blockchain = jsonpickle.loads(requests.get('http://' + self.sig_to_ip_map["all"][-1] + '/blockchain').text)

            st = input("Enter your SECP256k1 Signing Key in hex or else press enter:")  # use walrus
            if len(st) == 64:
                self.key = st
            else:
                self.key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512).to_string().hex()
            self.save(appfile)

    def add_transaction(self, trans): # to clean after completing tests live
        self.pending_trans["pending_list"].append(trans)
        if self.pending_trans["processing_thread"] is not None:
            if self.pending_trans["processing_thread"].is_alive():
                print("miner is running")
                return
            print("stopping miner")
            self.pending_trans["run_signal"][0] = False
            self.pending_trans["processing_thread"].join()
            print("mines is alive? " + str(self.pending_trans["processing_thread"].is_alive()))
        #remaking thread
        if hasattr(self.pending_block, 'status'):
            print("pending block was not completly mined?  block "+ self.pending_block.hash)
            print("status is " + str(self.pending_block.status))
        if isinstance(self.pending_block, Block):
            print("was not block")
            self.pending_block = Block(data=self.pending_trans["pending_list"])
        self.pending_block.previous_hash = self.blockchain.chain[-1].hash
        self.pending_block.status = "being mined"
        self.pending_trans["run_signal"][0] = True
        t1 = threading.Thread(target=self.pending_block.minenonce, kwargs={'miner': self.ver_key, 'run_signal': self.pending_trans["run_signal"]})
        t1.mined_block = self.pending_block # remove?
        t2 = threading.Thread(target=self.wait_for_mine_complete, kwargs={'thread': t1})
        t1.start()
        t2.start()
        self.pending_trans["processing_thread"] = t1

    def wait_for_mine_complete(self, thread):
        thread.join()
        if  self.blockchain.chain[-1].hash == self.pending_block.previous_hash and self.pending_block.validhash:
            print("HELLO WORLD HERE IS SUCESS MINE")
            self.blockchain.chain.append(copy.deepcopy(self.pending_block))
            for trans_comp in self.blockchain.chain[-1].data:
                for trans in self.pending_trans["pending_list"]:
                    if json.dumps(trans_comp, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True) == json.dumps(trans, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True):
                        #if trans_comp.hash ==  trans.hash:
                        self.pending_trans["pending_list"].remove(trans)
        for x in this_app.sig_to_ip_map["all"]:
            print(("sending to http://" + x + "/receive_mined_block"))
            r = requests.get("http://" + x + "/receive_mined_block", params={"block": repr(self.blockchain.chain[-1])})  # r = requests.get("http://localhost:"+str(args.port)+"/")
            print(r.text)
        print("sended to all")


    def receive_block(self, block):
        print("recived block with hash " + str(block.hash))
        print("recived block with prevhash " + str(block.previous_hash))
        i = self.blockchain.findblockplace(block)
        if i is None:
            print("this block has no place here")
            return False
        print("this block belongs in " + str(i)+" index"+ "   when last index is " + str(len(self.blockchain.chain)-1))
        if i < len(self.blockchain.chain):
            if self.blockchain.chain[i].validhash:
                print("but we already have valid")
                if block.hash == self.blockchain.chain[i].hash:
                    print("print and they are the same")
                    return True
                return False
            else:
                print("ok but we have invalid there block number ")
                self.blockchain.chain[i] = copy.deepcopy(block) #deep copy when
        else:
            print("This block belongs in the end")
            self.blockchain.chain.append(copy.deepcopy(block))
        print("trans added")
        print(self.pending_trans)
        print("trans pending")
        print(self.pending_trans["pending_list"])
        for trans_comp in self.blockchain.chain[-1].data:
            for trans in self.pending_trans["pending_list"]:
                if json.dumps(trans_comp, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True) == json.dumps(trans, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True):
                    self.pending_trans["pending_list"].remove(trans)
        return True

    def propagate_new_block(self,out_block):
        for ip in self.sig_to_ip_map["all"]:
            with suppress(Exception):
                r = requests.get("http://"+ip + "/receive_mined_block", params={"block": repr(out_block)})
                print(r.text)
                print("sent to "+ ip)

    def propagate_new_transaction(self,out_trans):
        for ip in self.sig_to_ip_map["all"]:
            with suppress(Exception):
                r = requests.get("http://" + ip + "/add_transaction", params={"transaction": repr(out_trans)})
                print(r.text)
                print("sent to " + ip)

    def aquire_blockchain(self):
        recived_chains =[]
        for ip in self.sig_to_ip_map["all"]:
            with suppress(Exception):
                r = requests.get("http://" + ip + "/add_transaction")
                recived_chains.append(json.loads(r.text))
                print("from " + ip+" "+ len(recived_chains[-1]["chain"]) +"\n" + json.dumps(recived_chains[-1], indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True) )
        largest_chain = recived_chains[-1]
        for chain in recived_chains:
            if len(chain["chain"]) > len(largest_chain["chain"]):
                largest_chain = chain
        print("largest chain is "+json.dumps(largest_chain, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True))



    @property
    def ver_key(self):
        return ecdsa.SigningKey.from_string(bytes.fromhex(self.key), curve=ecdsa.SECP256k1, hashfunc=sha3_512).verifying_key.to_string().hex()

    def __repr__(self):
        return json.dumps(self, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True)


class Transaction:
    def __init__(self, data, sign=None, signer=None, sign_key=None):
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
        if self._hash != self.hash:
            return False
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
    def __init__(self, data=[], previous_hash=int(0).to_bytes(64, 'big').hex(), nonce=0, miner=("0" * 128), timestamp=None,diff=2):
        self.previous_hash = previous_hash
        self.data = data # restruct to arrays only
        self.miner = miner
        self.timestamp = timestamp if timestamp is not None else int(time.time())
        self.nonce = nonce
        self._hash = self.hash
        self.diff = diff

    def minenonce(self, miner=None, run_signal=(True,)):
        self.miner = miner if miner is not None else self.miner
        self.nonce = self.nonce #random.randint(0, 2 ** 30) if self.nonce == 0 else self.nonce
        while self.hash[0:self.diff] != ("0" * self.diff) and run_signal[0]:
            self.nonce += 1
            self.timestamp = int(time.time())
            # print(self.hash[0:diff]+"\n"+str(self.nonce)+"\n")
            # time.sleep(1)
            time.sleep(0.01)
        if not run_signal[0]:
            print("exit signal")
            self.status = "stopped mining"
            return self
        if hasattr(self, 'status'):
            delattr(self, 'status')
        return self

    @property
    def hash(self):
        self._hash = hashlib.sha3_512((self.previous_hash + repr(self.data) + self.miner).encode('ascii') + self.timestamp.to_bytes(32, 'big') + self.nonce.to_bytes(32, 'big')).hexdigest()
        return self._hash

    @property
    def validhash(self):
        return self._hash[0:self.diff] == ("0" * self.diff)


    def __repr__(self):
        return json.dumps(self, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True)


class BlockChain:
    def __init__(self, jsonrepr=None):
        if isinstance(jsonrepr, str):
            vars(self).update(json.loads(jsonrepr))
        else:
            self.chain = []
            self.boot()

    #def parse(self, jsonrepr):
     #   return json.loads(jsonrepr)

    def boot(self,sign_key=ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512).to_string().hex()):
        self.chain = [Block(data=[Transaction(["start",sign_key],sign_key=sign_key)]).minenonce(miner=("0" * 128))]

    def addblock(self, newblock: Block, ver_key=None):
        print(self.chain[-1].hash)
        newblock.previous_hash = self.chain[-1].hash
        self.chain.append(newblock.minenonce(miner=ver_key))

    def findblockplace(self,blocktocheck):
        for num, old_block in enumerate(self.chain):
            print("comapring " + str(old_block._hash))
            if blocktocheck.previous_hash == old_block._hash:
                print("this block belongs in " + str(num + 1))
                return num+1
        #return

    def load_dict_repr(self,repr_string):
        dict_repr = json.loads(repr_string)
        for index,block in enumerate(dict_repr["chain"]):
            new_block = Block()
            new_block.__dict__ = block
            if not new_block.validhash:
                print("block is invalid "+ repr(new_block))
                return False
            dict_repr["chain"][index] = new_block
            #print("block is valid " + repr(new_block))
            #print("block is valid " + repr(new_block.data))
            #print("block is valid " + type(new_block.data))

            for index, trans in enumerate(new_block.data):
                newtrans = Transaction(data =[])
                newtrans.__dict__ = trans
                if not newtrans.verify():
                    print("newtrans is invalid " + repr(newtrans))
                    return False
                new_block.data[index] = newtrans

        for x in dict_repr:
            print(str(type(x))+ " " + repr(x))
        for x in dict_repr["chain"]:
            print(str(type(x)) + " " + repr(x))
        self.__dict__ = dict_repr
        return True

    def validate(self):
        for i in range(1, len(self.chain)):
            if self.chain[i].previous_hash != self.chain[i - 1].hash:
                print("invalid hash on " + str(i) + "\n" + self.chain[i].previous_hash + "\n" + self.chain[i - 1].hash)
                return False
            for trans in self.chain[i].data:
                if not isinstance(trans,Transaction) or not trans.verify():
                    return False
        return True

    def __repr__(self):
        return json.dumps(self, indent=4, cls=JCoder, sort_keys=True, ensure_ascii=True)




@app.route('/')
def hello_world():
    # if request.remote_addr != "127.0.0.1":
    #   return 'Hello,'+request.remote_addr
    return render_template('manage.html', text=this_app.__repr__(), appdict=this_app.__dict__)  # .replace("\n","<br>\n")


@app.route('/change_key')
def changekey():
    if request.remote_addr != "127.0.0.1":
        return 'Hello,' + request.remote_addr + " not allowed", 404
    if request.args.get('key') is None:
        return this_app.key + " is still current key remains unchanged"
    this_app.key = request.args.get('key')
    return "changed key to " + this_app.key


@app.route('/add_ip')
def add_ip():
    if request.remote_addr != "127.0.0.1":
        return 'Hello,' + request.remote_addr + " not allowed", 404
    if request.args.get('ip') is None:
        return "no ip was sent"
    this_app.sig_to_ip_map["all"].append(request.args.get('ip'))
    return " addedd " + request.args.get('ip')


@app.route('/add_transaction')
def add_transaction():
    if request.args.get('transaction') is None:
        return "no transaction was sent"
    # "check if trasnaction is from self"
    # sign transaction
    # add to  mining block
    this_app.add_transaction(request.args.get('transaction'))
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
        print( request.args)
        return "no block was sent"
    # "check if trasnaction is from self"
    # sign transaction
    # add to  mining block
    #refactor this into  block rerpr to object
    try:
        dict_repr = json.loads(request.args.get('block'))
        print("inside recived block " + repr(dict_repr))
        new_block = Block()
        new_block.__dict__ = dict_repr
        print("data inside recived block " + repr(new_block.data))
        for index, trans in enumerate(new_block.data):
            newtrans = Transaction(data=[])
            print("data inside trans " + str(type(trans))+" "+repr(trans))
            newtrans.__dict__ = trans
            if not newtrans.verify():
                print("newtrans is invalid " + repr(newtrans))
                return False
            new_block.data[index] = newtrans
            success = this_app.receive_block(new_block)
            return "sucess = " + str(success)
    except Exception as e:
        return "error parsing " + str(e.value)

if __name__ == '__main__':
    # this_app = App(loadfile="current.app")
    # print(this_app)
    this_app = App()
    print(this_app)
    a = Transaction({"moviments": {"Fred": 10, "John": 20}, "time": int(time.time())}, sign_key=this_app.key)
    this_app.blockchain.addblock(Block(data=a), ver_key=this_app.ver_key)
    print(this_app)
    this_app.add_transaction(trans=["test"])
    # this_app.pending_trans["pending_list"].append(["data2"])
    # print(this_app)
    this_app.pending_trans["run_signal"][0] = False
    # print(this_app)
    print("status: " + str(this_app.blockchain.chain[-1].__dict__.get("status")))
    this_app.pending_trans["processing_thread"].join()
    print(this_app)
    inc_block = Block(data=[["test"]], previous_hash=this_app.blockchain.chain[-1].hash).minenonce()
    print("printing incoming block")
    print(inc_block)
    print(this_app)


    # this_app.receive_block(inc_block)

    def test():
        time.sleep(13)
        print(("http://localhost:" + str(args.port) + "/receive_mined_block"))
        r = requests.get("http://localhost:" + str(args.port) + "/receive_mined_block", params={"block": repr(inc_block)})  # r = requests.get("http://localhost:"+str(args.port)+"/")
        print(r.text)
        print("printing app after recieving")
        print(this_app)
        print(this_app.pending_trans["processing_thread"].mined_block)


    threading.Thread(target=test).start()

    app.run(host='0.0.0.0', port=args.port)#, debug=True)
