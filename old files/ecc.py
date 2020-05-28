import ecdsa
from hashlib import sha256

# SECP256k1 is the Bitcoin elliptic curve
sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha256)
vk = sk.get_verifying_key()
sig = sk.sign(b"message")
print(vk.verify(sig, b"message")) # True



print(vk.verify(sig, b"message")) # True

b = sk.privkey

print(sk.privkey) # True
print(sk.__dict__)
print(sk.verifying_key) # True.
print(sk.to_pem()) # True
print(sk.verifying_key.to_pem()) # True.
print(sk.to_string().hex()) # True
print(sk.privkey) # True

print(sk.verifying_key.to_string().hex()) # True.
print(len(sk.verifying_key.to_string())) # True.

strkey = sk.verifying_key.to_string().hex()

vk2 = ecdsa.VerifyingKey.from_string(bytes.fromhex(strkey), curve=ecdsa.SECP256k1, hashfunc=sha256) # the default is sha1

print(vk2.verify(sig, b"message")) # True

#ecdsa.SigningKey.privkey
sk2 = ecdsa.SigningKey.from_string(sk.to_string(), curve=ecdsa.SECP256k1)
print(sk2.to_string().hex()) # True







