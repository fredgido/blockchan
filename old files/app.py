



import hashlib
import json
import time
import os
import copy
import random

random.seed(0)

import ecdsa
from hashlib import sha3_512


class JCoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__


# def to_dict(obj):
# return json.loads(json.dumps(obj, default=lambda o: o.__dict__))

class App:
    def __init__(self, blockchain=None, sig_to_ip_map=None, key=None, load=None):
        self.blockchain = blockchain
        self.sig_to_ip_map = sig_to_ip_map
        self.key = self.load_key() if key is None else key
        self.__dict__ = json.loads(load) if load is not None else self.__dict__

    def load_key(self, file="key.sk"):
        if os.path.isfile(file):
            with open(file, "rb") as f:
                return f.read().hex()
                # sk = ecdsa.SigningKey.from_string(read, curve=ecdsa.SECP256k1, hashfunc=sha3_512)
        else:
            # self.key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512).to_string()
            with open(file, "wb") as f:
                f.write(ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512).to_string())
    @property
    def ver_key(self):
        return ecdsa.SigningKey.from_string(bytes.fromhex(self.key), curve=ecdsa.SECP256k1, hashfunc=sha3_512).verifying_key.to_string().hex()

    def __repr__(self):
        return json.dumps(self, indent=4, cls=JCoder)


class Transaction:
    def __init__(self, data, sign=None, signer=None):
        self.data = data
        self.sign = sign
        self.signer = signer
        # self._hash = self.hash

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
        print("calc trans hash")
        return hashlib.sha3_512(json.dumps(self.data, sort_keys=True, ensure_ascii=True).encode('ascii')).hexdigest()

    def __repr__(self):
        return json.dumps(self, indent=4, cls=JCoder)


class Block:
    def __init__(self, data, previous_hash=int(0).to_bytes(64, 'big').hex(), nonce=0, miner=("0" * 128), timestamp=None):
        self.previous_hash = previous_hash
        self.data = data
        self.miner = miner
        self.timestamp = timestamp if timestamp is not None else int(time.time())
        self.nonce = nonce
        self._hash = self.hash

    def minenonce(self, diff=2, miner=None):
        self.miner = miner if miner is not None else self.miner
        self.nonce = random.randint(0, 2 ** 30) if self.nonce ==0 else self.nonce
        while self.hash[0:diff] != ("0" * diff):
            self.nonce += 1
            self.timestamp = int(time.time())
            # print(self.hash)
            # print(self.hash[0:diff])
            # print("0" * diff)
            # print(self.nonce)
            # print()
            #time.sleep(1)
        print(self._hash)
        print(self.hash[0:diff])
        print(("0" * diff))
        print(self.hash)
        print(self._hash)
        print(self.hash[0:diff])
        print(("0" * diff))

        return self

    @property
    def hash(self):
        #print("calchash")
        #return hashlib.sha3_512((self.previous_hash + repr(self.data) + self.miner).encode('ascii') + bytes(self.timestamp) + bytes(self.nonce)).hexdigest()
        self._hash = hashlib.sha3_512((self.previous_hash + repr(self.data) + self.miner).encode('ascii')+ self.timestamp.to_bytes(32,'big')+ self.nonce.to_bytes(32,'big')).hexdigest()
        return self._hash




    def __repr__(self):
        return json.dumps(self, indent=4, cls=JCoder)


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

    def addblock(self, newblock: Block):
        print(self.chain[-1].hash)
        newblock.previous_hash = self.chain[-1].hash
        self.chain.append(newblock.minenonce(miner=self.ver_key))

    def validate(self):
        for i in range(1, len(self.chain)):
            if self.chain[i].previous_hash != self.chain[i - 1].hash:
                print("invalid hash on " + str(i) + "\n" + self.chain[i].previous_hash + "\n" + self.chain[i - 1].hash)
                return False
        return True

    def __repr__(self):
        return json.dumps(self, indent=4, cls=JCoder)

this_app = App(blockchain=BlockChain(), sig_to_ip_map={"all": []})
print(this_app)
print(this_app.blockchain.chain[-1].hash)
print(this_app.blockchain.chain[-1].__dict__)




a = Transaction({"moviments": {"Fred": 10, "John": 20}, "time": int(time.time())})
print(a)
print(a.verify())
a.signit(this_app.key)
print(a)
print(a.verify())

new_block = Block(data=a)
#new_block.minenonce()

this_app.blockchain.addblock(new_block)
print(new_block)
new_block2 = Block(data="banana")
#new_block2.minenonce()

this_app.blockchain.addblock(new_block2)

print(this_app)

