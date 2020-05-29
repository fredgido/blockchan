import webapp
from webapp import *
import sys
import io


import subprocess
if args.port == 8333:
    subprocess.Popen(["python",'test6.py', '--port','8334'])

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
    if args.port != 8333:
        this_app.blockchain = BlockChain()
        def test():
            time.sleep(10)
            print(this_app)
            print(("http://localhost:" + str(args.port-1) + "/blockchain"))
            r = requests.get("http://localhost:" + str(args.port-1) + "/blockchain")
            print("printing app after recieving")

            print(json.loads(r.text))
            print("loaded? "+str(this_app.blockchain.load_dict_repr(r.text)))
            print(this_app)
            print("Is block chain vlaid? "+str(this_app.blockchain.validate()))
            # print(this_app.pending_trans["processing_thread"].mined_block)


        threading.Thread(target=test).start()
        app.run(host='0.0.0.0', port=args.port)  # , debug=True)
    else:
        print(str(args.port)+repr(this_app))

        app.run(host='0.0.0.0', port=args.port)  # , debug=True)





