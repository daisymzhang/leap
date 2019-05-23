package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"google.golang.org/grpc"
	"io/ioutil"
	pb "leap/ProtoBuf"
	"net"
	"os"
	"time"
)

var (
	config Config
	siteConnectors = make(map[AlgoId]map[SiteId]string) // Map of available algos with a map of the ip and port of the site connectors with that algo as a value
	cloudAlgos = make(map[AlgoId]string) // Map of available algos in the cloud
)

type AlgoId int32
type SiteId int32

type Message struct {
	msg string
}

type Config struct {
	ListenCloudIpPort string
	ListenSiteIpPort  string
	Sites       string
}

type CloudCoordinatorService struct{}
type SiteCoordinatorService struct{}

/*
Parses user flags and creates config using the given flags.
If a flag is absent, use the default flag given in the
config.json file.

No args.
 */
func InitializeCoordinator() {
	jsonFile, err := os.Open("config.json")
	checkErr(err)
	defer jsonFile.Close()
	jsonBytes, err := ioutil.ReadAll(jsonFile)
	checkErr(err)

	err = json.Unmarshal(jsonBytes, &config)
	checkErr(err)

	CloudIpPortPtr := flag.String("cip", config.ListenCloudIpPort, "The ip and port the coordinator is listening for cloud connections")
	SiteIpPortPtr := flag.String("sip", config.ListenSiteIpPort, "The ip and port the coordinator is listening for site connections")
	flag.Parse()

	config.ListenCloudIpPort = *CloudIpPortPtr
	config.ListenSiteIpPort = *SiteIpPortPtr
	siteConnectors[0] = make(map[SiteId]string)
	siteConnectors[0][0] = "127.0.0.1:50003"
	// algos[0][1] = true
}

func (s *SiteCoordinatorService) RegisterAlgo(ctx context.Context, req *pb.SiteAlgoRegReq) (*pb.SiteAlgoRegRes, error) {
	return nil, nil
}

func (s *CloudCoordinatorService) RegisterAlgo(ctx context.Context, req *pb.CloudAlgoRegReq) (*pb.CloudAlgoRegRes, error) {
	return nil, nil
}

/*
Makes a remote procedure call to a site connector with a
query and returns the result of computing the query on a
site algorithm.

ctx: Carries value and cancellation signals across API
     boundaries.
req: Request created by algorithm in the cloud.
 */
func (s *CloudCoordinatorService) Compute(ctx context.Context, req *pb.ComputeRequest) (*pb.ComputeResponses, error) {
	fmt.Println("Coordinator: Compute request received")
	sites := siteConnectors[AlgoId(req.AlgoId)]
	var results pb.ComputeResponses
	for _, ipPort := range sites {
		conn, err := grpc.Dial(ipPort, grpc.WithInsecure())
		checkErr(err)
		defer conn.Close()
		c := pb.NewCoordinatorConnectorClient(conn)
		ctx, cancel := context.WithTimeout(context.Background(), time.Second)
		defer cancel()
		localResponse, err := c.Compute(ctx, req)
		checkErr(err)
		results.Responses = append(results.Responses, localResponse)
	}

	return &results, nil
}

/*
Serves RPC calls from sites.

No args.
*/
func ListenSites() {
	listener, err := net.Listen("tcp", config.ListenSiteIpPort)
	checkErr(err)
	fmt.Println("Coordinator: Listening for site connectors at", config.ListenSiteIpPort)
	s := grpc.NewServer()
	pb.RegisterSiteCoordinatorServer(s, &SiteCoordinatorService{})
	err = s.Serve(listener)
	checkErr(err)
}

/*
Serves RPC calls from cloud algorithms.

No args.
*/
func ListenCloud() {
	listener, err := net.Listen("tcp", config.ListenCloudIpPort)
	checkErr(err)
	fmt.Println("Coordinator: Listening for cloud algos at", config.ListenCloudIpPort)
	s := grpc.NewServer()
	pb.RegisterCloudCoordinatorServer(s, &CloudCoordinatorService{})
	err = s.Serve(listener)
	checkErr(err)
}

/*
Helper to log errors in the coordinator.

err: Error returned by a function that should be checked
     if nil or not.
*/
func checkErr(err error) {
	if err != nil {
		fmt.Println("Coordinator:", err.Error())
	}
}