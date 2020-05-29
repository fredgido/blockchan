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

    this_app.boot("test9"+str(args.port)+".app")
    os.remove("test9"+str(args.port)+".app")
    #with open("test5.app","r") as f:
    #    print("\nfile:")
    #    print(f.read())
    #os.remove("test5.app")
    for x in range(8333 + 1, 8333 + 15):
        this_app.sig_to_ip_map["all"].append("localhost:" + str(x))

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
            list = copy.deepcopy(this_app.sig_to_ip_map["all"])
            while(len(list)>0):
                try:
                    r = requests.get("http://" + list[0] + "/key")  # r = requests.get("http://localhost:"+str(args.port)+"/")
                    print(r.text)
                    list.remove(list[0])
                except:
                    time.sleep(1)

            print("wait end "+str(len(list)))
            this_app.receive_block(b)


            print("start sending")
            for x in this_app.sig_to_ip_map["all"]:
                print(("http://"+x + "/receive_mined_block"))
                r = requests.get("http://"+x + "/receive_mined_block", params={"block": repr(b)})  # r = requests.get("http://localhost:"+str(args.port)+"/")
                print(r.text)
                #time.sleep(1)
            time.sleep(5)
            print("end")


            this_app.add_transaction(Transaction("added"))
        t = threading.Thread(target=test)
        t.start()
    else:
        print("starting loading "+ str(args.port))
        r = requests.get("http://localhost:" + str(8333) + "/blockchain")  # r = requests.get("http://localhost:"+str(args.port)+"/")
        print(json.loads(r.text))
        print(str(args.port)+" loaded? " + str(this_app.blockchain.load_dict_repr(r.text)))


    app.run(host='0.0.0.0', port=args.port)  # , debug=True)





