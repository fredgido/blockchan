import webapp
from webapp import *
import sys
import io


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
    b = Block(data=a).minenonce()
    this_app.receive_block(b)

    def test():
        time.sleep(5)
        print(("http://localhost:" + str(args.port) + "/blockchain"))
        r = requests.get("http://localhost:" + str(args.port) + "/blockchain")
        print("printing app after recieving")
        print(r.text)
        #print(this_app)
        #print(this_app.pending_trans["processing_thread"].mined_block)


    threading.Thread(target=test).start()


    app.run(host='0.0.0.0', port=args.port)#, debug=True)
