import webapp
from webapp import *
import sys
import io


import subprocess



#test empty app
if __name__ == '__main__':
    webapp.time.time = lambda: 1337
    print(time.time())
    this_app = App()
    webapp.this_app = this_app
    print(webapp)
    sys.stdin = io.StringIO("0\nf9544621d18b3efb2f3492c678e25c9ceb61917999935d199b77674a8a5d5b42\n")
    this_app.boot("test5.app")
    with open("test5.app","r") as f:
        print("\nfile:")
        print(f.read())
    os.remove("test5.app")

    a = Transaction({"moviments": {"Fred": 10, "John": 20}, "time": int(time.time())}, sign_key=this_app.key)
    b = Block(data=[a],previous_hash=this_app.blockchain.chain[-1].hash).minenonce()
    this_app.receive_block(b)
    print("splitting")
    print(this_app)
    chain_srt = repr(this_app.blockchain)
    print(chain_srt)
    this_app.blockchain = BlockChain()
    this_app.blockchain.boot()
    print("starting loading")
    print("loaded? " + str(this_app.blockchain.load_dict_repr(chain_srt)))
    print(this_app)
    for block in this_app.blockchain.chain:
        print("_hash is "+block._hash+" and hash is "+block.hash)

    print(repr(b))
    print(repr(this_app.blockchain.chain[-1]))
    print(repr(b.data[0].hash))
    print(repr(this_app.blockchain.chain[-1].data[0].hash))
