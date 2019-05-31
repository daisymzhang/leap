import grpc
import time
import argparse
import concurrent.futures as futures
import sys
import google.protobuf.any_pb2 as any_pb2

# TODO: Find way to get rid of this ugly import
sys.path.append('../ProtoBuf')

import computation_msgs_pb2 as computation_pb2
import registration_msgs_pb2 as registration_pb2
import count_msgs_pb2 as count_pb2
import site_algos_pb2_grpc as site_algos_grpc
import site_connector_pb2_grpc as site_connector_grpc

patients = [{"fname": "Han", "lname": "Solo", "email": "hsolo@gmail.com", "age": 29, "gender": "male", "weight": 80, "height": 180},
            {"fname": "Mark", "lname": "Atlas", "email": "matlas@gmail.com", "age": 92, "gender": "male", "weight": 61, "height": 180},
            {"fname": "Joe", "lname": "Hum", "email": "jhum@gmail.com", "age": 85, "gender": "male", "weight": 72, "height": 184},
            {"fname": "Bill", "lname": "Blase", "email": "blase@gmail.com", "age": 22, "gender": "male", "weight": 85, "height": 174},
            {"fname": "Mary", "lname": "Swalino", "email": "mswalino@gmail.com", "age": 19, "gender": "female", "weight": 55, "height": 178},
            {"fname": "Milton", "lname": "Bo", "email": "mbo@gmail.com", "age": 19, "gender": "male", "weight": 78, "height": 186},
            {"fname": "Olivia", "lname": "Alos", "email": "oalos@gmail.com", "age": 30, "gender": "female", "weight": 50, "height": 160},
            {"fname": "Clarissa", "lname": "Vikander", "email": "cikander@gmail.com", "age": 41, "gender": "female", "weight": 61, "height": 155},
            {"fname": "Bruna", "lname": "Lorius", "email": "blorius@gmail.com", "age": 55, "gender": "female", "weight": 60, "height": 172},
            {"fname": "Anna", "lname": "Tu", "email": "atu@gmail.com", "age": 101, "gender": "female", "weight": 65, "height": 150}]

parser = argparse.ArgumentParser()
parser.add_argument("-id", "--algoId", default="0", help="The id of this algorithm")
parser.add_argument("-ip", "--ipPort", default="127.0.0.1:60000", help="The ip and port this algorithm is listening to")
parser.add_argument("-cip", "--connectorIpPort", default="127.0.0.1:50002", help="The ip and port the site connector is listening to")
args = parser.parse_args()

def register():
    with grpc.insecure_channel(args.connectorIpPort) as channel:
        stub = site_connector_grpc.AlgoConnectorStub(channel)
        req = registration_pb2.SiteAlgoRegReq()
        req.algo_id = int(args.algoId)
        req.description = "A count algorithm"
        req.proto_version = "proto3"
        req.algo_ip_port = args.ipPort
        response = stub.RegisterAlgo(req)
        if response.success:
            print("Site-Algo: Successfully registered algorithm with coordinator")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    site_algos_grpc.add_SiteAlgoServicer_to_server(SiteAlgoServicer(), server)
    server.add_insecure_port(args.ipPort)
    server.start()
    print("Site Algo " + args.algoId + ": Server started")
    print("Site Algo " + args.algoId + ": Listening at " + args.ipPort)

class SiteAlgoServicer(site_algos_grpc.SiteAlgoServicer):

    def compare(self, patientVal, queryVal, operator):
        if operator == "GT":
            return patientVal > queryVal
        elif operator == "LT":
            return patientVal < queryVal
        elif operator == "EQ":
            return patientVal == queryVal
        else:
            return False

    def count(self, query):
        count = 0
        for patient in patients:
            if query.field == "age":
                if self.compare(patient["age"], query.numeric_value, query.operator):
                    count += 1
            if query.field == "weight":
                if self.compare(patient["weight"], query.numeric_value, query.operator):
                    count += 1
            if query.field == "height":
                if self.compare(patient["height"], query.numeric_value, query.operator):
                    count += 1
        return count

    def Compute(self, request, context):
        print("Site-Algo: Got compute call")
        query = count_pb2.Query()
        if request.req.Is(query.DESCRIPTOR):
            request.req.Unpack(query)
        result = self.count(query)
        res = computation_pb2.ComputeResponse()
        int_response = computation_pb2.IntResponse()
        int_response.val = result
        any_res = any_pb2.Any()
        any_res.Pack(int_response)
        res.response.CopyFrom(any_res)
        return res

if __name__ == "__main__":
    serve()
    register()
    while True:
        time.sleep(5)
