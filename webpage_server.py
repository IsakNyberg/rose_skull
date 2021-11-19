# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

hostName = "192.168.10.150"
serverPort = 7878

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if self.path == "/":
            in_file = open(f"page/index.html", "rb") # opening for [r]eading as [b]inary
        else:
            in_file = open(f"page/{self.path}", "rb") # opening for [r]eading as [b]inary
        data = in_file.read() # if you only wanted to read 512 bytes, do .read(512)
        in_file.close()
        self.wfile.write(data)

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
