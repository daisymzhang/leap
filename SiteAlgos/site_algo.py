import sys
sys.path.append("../")
import pdb
import grpc
import time
import multiprocessing
import argparse
import concurrent.futures as futures
import redcap
import json
import ProtoBuf as pb
import logging
from pylogrus import PyLogrus, TextFormatter

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-ip", "--ip_port", default="127.0.0.1:60000", help="The ip and port this algorithm is listening to")
parser.add_argument("-cip", "--connector_ip_port", default="127.0.0.1:50001", help="The ip and port of the site connector")
args = parser.parse_args()

# Setup logging tool
logging.setLoggerClass(PyLogrus)
logger = logging.getLogger(__name__)  # type: PyLogrus
logger.setLevel(logging.DEBUG)
formatter = TextFormatter(datefmt='Z', colorize=True)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
log = logger.withFields({"node": "site-algo"})

redCapUrl = "https://rc.bcchr.ca/redcap_demo/api/"
redCapToken = "3405DC778F3D3B9639E53C1A3394EC09"

""" Contacts a redCap project and returns the filtered records from this project.

url: Url of the RedCap project
token: Token used to access RedCap project given in the url
filterLogic: The filter to be applied to the results."""
def getRedcapData(url, token, filterLogic):
    project = redcap.Project(url, token)
    patients = project.export_records(filter_logic=filterLogic)
    return patients

"""Starts listening for RPC requests at the specified ip and
port.

No args"""
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb.site_algos_pb2_grpc.add_SiteAlgoServicer_to_server(SiteAlgoServicer(), server)
    server.add_insecure_port(args.ip_port)
    server.start()
    log.info("Server started")
    log.info("Listening at " + args.ip_port)
    while True:
        time.sleep(5)

# RPC Service for Site Algos
class SiteAlgoServicer(pb.site_algos_pb2_grpc.SiteAlgoServicer):

    """ RPC requesting for a computation to be done using
    this algorithm.
    
    request: A protobuf request determining what to be
             computed
    context: Boilerplate for grpc containing the context
             of the RPC."""
    def Map(self, request, context):
        log.info("Got map request")
        req_id = request.id
        req = json.loads(request.req)

        exec(req["module"], globals())
        site_state = req["site_state"]
        s_filter = req["filter"]        
        choice = choice_fn(site_state)

        data = getRedcapData(redCapUrl, redCapToken, s_filter)
        if 'data_prep' in globals():
            data = data_prep(data)
            
        map_result = map_fn[choice](data, site_state)

        res = pb.computation_msgs_pb2.MapResponse()
        res.response = map_result
        return res

if __name__ == "__main__":
    serverProcess = multiprocessing.Process(target=serve)
    serverProcess.start()
