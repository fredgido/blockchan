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
    if args.port != 8333:
        sys.stdin = io.StringIO("0\nx\n")

    this_app.boot("test8.app")
    os.remove("test8.app")
    #with open("test5.app","r") as f:
    #    print("\nfile:")
    #    print(f.read())
    #os.remove("test5.app")


    print("splitting")
    if args.port == 8333:


        a = Transaction({"moviments": {"Fred": 10, "John": 20}, "time": int(time.time())}, sign_key=this_app.key)
        b = Block(data=[a], previous_hash=this_app.blockchain.chain[-1].hash).minenonce()

        def test():
            time.sleep(5)
            for x in range(8333 + 1, 8333 + 15):
                subprocess.Popen(["python", 'test8.py', '--port', str(x)])
                #time.sleep(1)

            print("wait for others setup")
            time.sleep(30)
            print("wait end")
            this_app.receive_block(b)


            print("start sending")
            for x in range(8333 + 1, 8333 + 15):
                print(("http://localhost:" + str(x) + "/receive_mined_block"))
                r = requests.get("http://localhost:" + str(x) + "/receive_mined_block", params={"block": repr(b)})  # r = requests.get("http://localhost:"+str(args.port)+"/")
                print(r.text)
                #time.sleep(1)

        t = threading.Thread(target=test)
        t.start()
    else:
        print("starting loading "+ str(args.port))
        r = requests.get("http://localhost:" + str(8333) + "/blockchain")  # r = requests.get("http://localhost:"+str(args.port)+"/")
        print(json.loads(r.text))
        print(str(args.port)+" loaded? " + str(this_app.blockchain.load_dict_repr(r.text)))


    app.run(host='0.0.0.0', port=args.port)  # , debug=True)





