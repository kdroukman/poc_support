from SimpleHTTPServer import SimpleHTTPRequestHandler
import SocketServer

PORT = 9080

class ServerHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/apm/metricFeed":
            content_len = int(self.headers.getheader('content-length', 0))
            post_body = self.rfile.read(content_len)
            self.send_response(200)
            self.end_headers()

            with open("layer7output.txt", "a") as outfile:
                outfile.write(post_body + "\n---\n")
                outfile.close()
        else:
            self.send_response(200)
            self.end_headers()
        return


httpd = SocketServer.TCPServer(("", PORT), ServerHandler)

print "Serving at port", PORT
httpd.serve_forever()





