import hashlib
import time
import json
import pprint


class Block:
    def __init__(self, index, data, previous_hash = int(0).to_bytes(64,'big').hex(),nonce=0, proof=None):
        self.index = index
        self.proof = proof
        self.data = data
        self.nonce = self.minenonce() if int(previous_hash,16) != 0 else 0
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self._hash = self.hash


    def minenonce(self,diff=1):
        while self.hash[0:diff] != ("0" * diff):
            self.nonce += 1
            print(self.hash)
            print(self.hash[0:diff])
            print("0" * diff)
            print(self.nonce)

            print()

            time.sleep(1)

        return self.nonce

    @property
    def previous_hash(self):
        return self.__previouhash

    @previous_hash.setter
    def previous_hash(self, value):
        self.minenonce()
        self.__previouhash = value



    @property
    def hash (self):
        print("calchash")
        return hashlib.sha3_512(self.data.encode('utf-8')+bytes(self.nonce)).hexdigest()

    def __repr__(self):
        return pprint.PrettyPrinter(indent=4).pformat(self.__dict__)


class BlockChain:
    def __init__(self, jsonrepr=None):
        if isinstance(jsonrepr, str):
            vars(self).update(dict)
        else:
            self.chain = [self.boot()]

    def parse(self, jsonrepr):
        return json.loads(jsonrepr)

    def boot(self):
        return Block(index=0, data="start")

    def addblock(self,newblock : Block):
        newblock.previous_hash = self.chain[-1].hash
        self.chain.append(newblock)

    def validate(self):
        for i in range(1,len(self.chain)):
            if self.chain[i].previous_hash != self.chain[i-1].hash:
                print("invalid hash on "+str(i)+"\n"+ self.chain[i].previous_hash+ "\n"+self.chain[i-1].hash)
                return False
        return True

    def __repr__(self):
        return pprint.PrettyPrinter(indent=4).pformat(self.__dict__)

a = Block(index=0, previous_hash=int(0).to_bytes(64, 'big').hex(), data="start")

print(a.hash)
print(hashlib.sha3_512(a.hash.encode('utf-8')).hexdigest())
print(hashlib.sha3_512(a.hash.encode('utf-8')).digest())
print(bytes.fromhex((hashlib.sha3_512(a.hash.encode('utf-8')).hexdigest())).hex())
print(repr(bytes.fromhex((hashlib.sha3_512(a.hash.encode('utf-8')).hexdigest()))))

print(len(hashlib.sha3_512(a.hash.encode('utf-8')).digest()))
print(int(16).to_bytes(64, 'big'))
print(repr(a))
#pp.pprint(a)

chain = BlockChain()
print(chain)
print("\n\n")
chain.addblock(Block(index=1, data="next"))
chain.addblock(Block(index=2, data="next2"))

print(chain)
print(chain.validate())
print(chain.chain[0].minenonce())




