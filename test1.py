import webapp
from webapp import *

if __name__ == '__main__':
    webapp.time.time = lambda: 1337

    # this_app = App(loadfile="current.app")
    # print(this_app)
    this_app = App()
    print(webapp)
    webapp.this_app = this_app
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
