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
    this_app.boot("test2.app")
    with open("test2.app","r") as f:
        print(f)
    os.remove("test2.app")

    app.run(host='0.0.0.0', port=args.port)#, debug=True)
