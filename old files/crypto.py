import hashlib
import json
import time
import os
import ecdsa
from hashlib import sha3_512



class Transaction:
    def __init__(self, data, sign = None, signer = None):
        self.data = data
        self.sign = sign
        self.signer = signer
        #self._hash = self.hash

    def signit(self,sk):
        self.sign = sk.sign(json.dumps(self.data, sort_keys=True, ensure_ascii=True).encode('ascii')).hex()
        self.signer = sk.verifying_key.to_string().hex()
        return True

    def verify(self):
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(self.signer), curve=ecdsa.SECP256k1, hashfunc=sha3_512)
        return vk.verify(bytes.fromhex(self.sign), json.dumps(self.data, sort_keys=True, ensure_ascii=True).encode('ascii'))

    @property
    def hash (self):
        print("calc trans hash")
        return hashlib.sha3_512(json.dumps(self.data, sort_keys=True, ensure_ascii=True).encode('ascii')).hexdigest()

    def __repr__(self):
        if self.__dict__ != json.loads(json.dumps(self.__dict__, indent=4)):
            print("error not representable")
        return json.dumps(self.__dict__, indent=4)


a = Transaction({"moviments": {"Fred": 10, "John": 20}, "time": int(time.time())})
a.hash

print(a)

if os.path.isfile("key.sk"):
    with open("key.sk","rb") as f:
        read = f.read()
        print(read)
        sk = ecdsa.SigningKey.from_string(read, curve=ecdsa.SECP256k1, hashfunc=sha3_512)
else:
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512)
    with open("key.sk","wb") as f:
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512)
        f.write(sk.to_string())


print(sk.to_string().hex())

print(sk.verifying_key.to_string().hex())

#json.dumps(a.data, sort_keys=True, ensure_ascii=True).encode('ascii')
a.signit(sk)

print(a)

print(a.verify())



#print(a)


