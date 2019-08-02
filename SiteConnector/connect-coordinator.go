package siteconnector

import (
	"context"
	"github.com/sirupsen/logrus"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"leap/Errors"
	pb "leap/ProtoBuf"
)

// Invokes map function in site and returns the result of run-
// ning the function on the local data.
//
// ctx: Carries value and cancellation signals across API
//      boundaries.
// req: Map request containing user defined functions.
func (sc *SiteConnector) Map(ctx context.Context, req *pb.MapRequest) (*pb.MapResponse, error) {
	sc.Log.WithFields(logrus.Fields{"request-id": req.Id}).Info("Received map request.")
	sc.PendingRequests.Set(req.Id, req.Id)
	conn, err := grpc.Dial(sc.Conf.AlgoIpPort, grpc.WithInsecure())

	checkErr(sc, err)
	defer conn.Close()

	client := pb.NewSiteAlgoClient(conn)
	res, err := client.Map(context.Background(), req)

	if Errors.IsUnavailableError(err) {
		sc.Log.WithFields(logrus.Fields{"request-id": req.Id}).Warn("Site Algo is unavailable.")
		checkErr(sc, err)
		return nil, status.Error(codes.Unavailable, "Site algo is unavailable")
	}

	checkErr(sc, err)
	return res, err
}
