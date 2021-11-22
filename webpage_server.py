# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import sys

path_lookup = {
    "/": "page/index.html",
    "/jspack.js": "page/jspack.js",
    "/back.png": "page/back.png",
    "/blank.png": "page/blank.png",
    "/rose.png": "page/rose.png",
    "/skull.png": "page/skull.png",
    "/favicon.ico": "page/favicon.ico",
    "/invisible.png" : "page/invisible.png",
    "/background.png" : "page/background.png",
}

content_lookup = {
    "/jspack.js" : "text/jscript",
    "/back.png" : "image/png",
    "/blank.png" : "image/png",
    "/rose.png" : "image/png",
    "/skull.png" : "image/png",
    "/invisible.png" : "image/png",
    "/" : "text/html",
    "/favicon.ico" : "image/x-icon",
    "/background.png" : "image/png",
}


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            in_file = open(path_lookup[self.path], "rb")
            content_type = content_lookup[self.path]
            data = in_file.read()
        except KeyError:
            self.send_response(400)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()
        in_file.close()
        self.wfile.write(data)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('usage: python3 webpage_server.py local_ip port')
        sys.exit()

    hostName = sys.argv[1]
    serverPort = int(sys.argv[2])
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
