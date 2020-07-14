from SimpleHTTPServer import SimpleHTTPRequestHandler
import SocketServer
import time

PORT = 9080

class ServerHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        self.send_response(200)
        self.end_headers()

        with open("layer7output_v3.txt", "a") as outfile:
            outfile.write(self.path + ": " + time.strftime("%Y%m%d-%H%M%S") + post_body + "\n---\n")
            outfile.close()


httpd = SocketServer.TCPServer(("", PORT), ServerHandler)

print "Serving at port", PORT
httpd.serve_forever()





