package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"google.golang.org/grpc"
	"io/ioutil"
	pb "leap/protoBuf"
	"net"
	"os"
	"time"
)

var (
	config Config
	algos = make(map[AlgoId]map[SiteId]string) // Map of available algos with a map of the sites with that algo as a value
)

type AlgoId int32
type SiteId int32

type Message struct {
	msg string
}

type Config struct {
	CloudIpPort string
	SiteIpPort string
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

	CloudIpPortPtr := flag.String("cip", config.CloudIpPort, "The ip and port the coordinator is listening for cloud connections")
	SiteIpPortPtr := flag.String("sip", config.SiteIpPort, "The ip and port the coordinator is listening for site connections")
	flag.Parse()

	config.CloudIpPort = *CloudIpPortPtr
	config.SiteIpPort = *SiteIpPortPtr
	algos[0] = make(map[SiteId]string)
	algos[0][0] = "127.0.0.1:60000"
	// algos[0][1] = true
}

func (s *SiteCoordinatorService) RegisterSite(ctx context.Context, req *pb.SiteRegReq) (*pb.SiteRegRes, error) {
 return nil, nil
}

func (s *SiteCoordinatorService) RegisterSiteAlgo(ctx context.Context, req *pb.SiteAlgoRegReq) (*pb.SiteAlgoRegRes, error) {
	return nil, nil
}

func (s *CloudCoordinatorService) RegisterCloudAlgo(ctx context.Context, req *pb.CloudAlgoRegReq) (*pb.CloudAlgoRegRes, error) {
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
func (s *CloudCoordinatorService) AlgoRequest(ctx context.Context, req *pb.ComputeRequest) (*pb.ComputeResponses, error) {
	fmt.Println("Coordinator: Compute request received")
	sites := algos[AlgoId(req.AlgoId)]
	var results pb.ComputeResponses
	for _, ipPort := range sites {
		conn, err := grpc.Dial(ipPort, grpc.WithInsecure())
		checkErr(err)
		defer conn.Close()
		c := pb.NewCoordinatorConnectorClient(conn)
		ctx, cancel := context.WithTimeout(context.Background(), time.Second)
		defer cancel()
		localResponse, err := c.AlgoRequest(ctx, req)
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
	listener, err := net.Listen("tcp", config.SiteIpPort)
	checkErr(err)
	fmt.Println("Coordinator: Listening for site connectors at", config.SiteIpPort)
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
	listener, err := net.Listen("tcp", config.CloudIpPort)
	checkErr(err)
	fmt.Println("Coordinator: Listening for cloud algos at", config.CloudIpPort)
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