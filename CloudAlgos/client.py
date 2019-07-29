import grpc
import argparse
import sys
sys.path.append("../")
import pdb
import json

import inspect

import CloudAlgos.functions.count_fn as count_fn

import ProtoBuf as pb
# pb.computation_msgs_pb2

parser = argparse.ArgumentParser()
parser.add_argument("-cip", "--cloud_algos_ip_port", default='127.0.0.1:70000', help="The ip and port of the cloudAlgos")
args = parser.parse_args()


class Client():
    def __init__(self, ipPort):
        print("Initializing Client")
        self.cloud_algos_ip_port = ipPort


    def _create_computation_request(self, u_module, filter):
        request = pb.computation_msgs_pb2.ComputeRequest()
        req = {}
        req["module"] = u_module
        req["filter"] = filter
        request.req = json.dumps(req)
        return request


    def send_request(self, u_module, filter):
        print("Sending request from client")
        # Sets up the connection so that we can make RPC calls
        with grpc.insecure_channel(args.cloud_algos_ip_port) as channel:
            stub = pb.cloud_algos_pb2_grpc.CloudAlgoStub(channel)

            req = self._create_computation_request(u_module, filter)

            result = stub.Compute(req) # Computed remotely

            if hasattr(result, "err"):
                print(result.err)

            result = json.loads(result.response)


            print("Received response")
            print(result)
        return result


def client_request():
    # Create connector. TODO: Decide how client request will talk to connector
    client = Client(args.cloud_algos_ip_port)

    # Get source code for map, agg, update, etc
    module = inspect.getsource(count_fn)
    filter = "[age] > 50 and [bmi] < 25"
    client.send_request(module, filter)


if __name__ == "__main__":
    client_request()
