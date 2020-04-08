from SimpleHTTPServer import SimpleHTTPRequestHandler
import SocketServer
import time
import argparse
import logging
import ConfigParser
import json
import requests
import re

def process_args():
    parser = argparse.ArgumentParser(description='Splunk SignalFx Layer7 Metrics Forwarder')
    parser.add_argument('-c','--config', help='forwarder configuration file', required=True)
    parser.add_argument('-t','--token', help='signalfx access token', required=True)
    return parser.parse_args()

# Apply Configuration
args = process_args()
config = ConfigParser.RawConfigParser()
config.read(args.config)

port = config.get('Server','port')

realm = config.get('SignalFx','realm')
sfx_token = args.token
service = config.get('SignalFx', 'service')
version = config.get('SignalFx', 'version')
env = config.get('SignalFx', 'env')

log_file = config.get('Logging','file')
dopost = bool(config.get('SignalFx','dopost'))

logging.basicConfig(filename=log_file, filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Loaded config(" + "service-" + service + ",version-" + version + ",realm-" + realm + ",env-" + env + ")")


# Post metric data to SignalFx
class SFxHandler():
    def __init__(self, r,t):
        self.realm = r
        self.token = t
        self.endpoint_dp = 'https://ingest.'+r+'.signalfx.com/v2/datapoint'
        self.endpoint_tags = 'https://api.'+r+'.signalfx.com/v2/dimension'
        self.headers = {
            'Content-Type': 'application/json',
            'X-SF-TOKEN': t
         }

    def post_dp(self,dp):
        r = requests.post(self.endpoint_dp,headers=self.headers, json=dp)
        if r.status_code != 200:
            logging.error("Bad Request:" + r.status_code)

    def put_tags(self, tags, dk, dv):
        r = requests.put(self.endpoint_tags + '/' + dk + '/' + dv, headers=self.headers, json=tags)
        if r.status_code != 200:
            logging.error("Bad Request:" + r.status_code)


# Convert Layer7 v 9.3 APM Metrics to SignalFx datapoints
def front_end_avg_response_time(dims, value):
    return {"gauge": [{
        "metric": "FrontEndAvgResponseTime.ms",
        "dimensions": {"host": dims[0], "service_uri": dims[5]},
        "value": value}
    ]}


def back_end_avg_response_time(dims, value):
    return {"gauge": [{
        "metric": "BackEndAvgResponseTime.ms",
        "dimensions": {"host": dims[0], "service_uri": dims[5]},
        "value": value}
    ]}


def request_size(dims, value):
    return {"gauge": [{
        "metric": "RequestSize.bytes",
        "dimensions": {"host": dims[0], "service_uri": dims[5]},
        "value": value}
    ]}


def response_size(dims, value):
    return {"gauge": [{
        "metric": "ResponseSize.bytes",
        "dimensions": {"host": dims[0], "service_uri": dims[5]},
        "value": value}
    ]}


def success_count(dims, value):
    return {"counter": [{
        "metric": "SuccessCount",
        "dimensions": {"host": dims[0], "service_uri": dims[5]},
        "value": value}
    ]}


def total_requests(dims, value):
    return {"counter": [{
        "metric": "TotalRequests",
        "dimensions": {"host": dims[0], "service_uri": dims[5]},
        "value": value}
    ]}


def get_sfx_json(metric_name, dims, value):
    return {
       "Front End Average Response Time (ms)" : front_end_avg_response_time(dims, value),
       "Back End Average Response Time (ms)" : back_end_avg_response_time(dims, value),
       "Request size (bytes)" : request_size(dims, value),
       "Response size (bytes)" : response_size(dims, value),
       "Success Count" : success_count(dims, value),
       "Total Requests" : total_requests(dims, value)
     }[metric_name]


def get_sfx_tags(dv,dk):
    return {
        "key": dv,
        "value": dk,
        "tags": [],
        "customProperties": {
            "namespace": service,
            "version": version,
            "env": env
        }
    }


def l72sfx(metric_data):
    data = json.loads(metric_data)
    sfx_datapoints = []
    host = ''
    for k,v in data.items():
        if isinstance(v, list):
            for i in v:
                # Identify Service metric elements
                if 'Services' in i['name']:
                    # Get Dimensions
                    dims = re.findall("[\w\-.*/() ]+", i['name'])
                    # Get the Layer 7 provided names
                    host = dims[0]
                    metric_name  = dims[6]
                    # Convert Layer 7 metric name to SignalFx metric format
                    sfx_datapoints.append(get_sfx_json(metric_name,dims,i['value']))
    return sfx_datapoints, host


sfxh = SFxHandler(realm,sfx_token)


class ServerHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        self.send_response(200)
        self.end_headers()

        dps, host = l72sfx(post_body)
        if dopost:
            for dp in dps:
                sfxh.post_dp(dp)
            sfxh.put_tags(get_sfx_tags("host",host),"host",host)


def run(port):
    httpd = SocketServer.TCPServer(("", port), ServerHandler)
    httpd.serve_forever()


logging.info("Serving at port ", port)
run(int(port))

