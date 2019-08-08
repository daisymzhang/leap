import sys
sys.path.append("../")
import pdb
import LeapApi.leap as leap
import LeapApi.leap_fn as leap_fn
import LeapApi.codes as codes
import CloudAlgo.functions as functions

import torch

class LinearModel(torch.nn.Module):
    def __init__(self, d, len_y):
        super(LinearModel, self).__init__()
        self.linear = torch.nn.Linear(d, len_y)

    def forward(self, x):
        out = self.linear(x)
        return out

def predef_count_exp():
    leap_udf = leap_fn.PredefinedFunction(codes.COUNT_ALGO)
    selector = "[age] > 50 and [bmi] < 25"
    leap_udf.selector = selector
    dist_leap = leap.DistributedLeap(leap_udf)
    dist_leap.send_request()

def udf_count_exp():
    leap_udf = leap_fn.UDF()
    module = functions.count_fn
    leap_udf.map_fns = module.map_fns
    leap_udf.update_fns = module.update_fns
    leap_udf.agg_fns = module.agg_fns
    leap_udf.choice_fn = module.choice_fn
    leap_udf.stop_fn = module.stop_fn
    leap_udf.dataprep_fn = module.dataprep_fn
    leap_udf.postprocessing_fn = module.postprocessing_fn
    leap_udf.init_state_fn = module.init_state_fn

    selector = "[age] > 50 and [bmi] < 25"
    leap_udf.selector = selector
    dist_leap = leap.DistributedLeap(leap_udf)
    dist_leap.send_request()

def fed_learn_exp():
    module = functions.fl_fn
    selector = "[age] > 50 and [bmi] < 25"
    leap_fed_learn = leap_fn.FedLearnFunction()
    leap_fed_learn.selector = selector
    leap_fed_learn.get_model = module.get_model
    leap_fed_learn.get_optimizer = module.get_optimizer
    leap_fed_learn.get_criterion = module.get_criterion
    leap_fed_learn.get_dataloader = module.get_dataloader
    hyperparams = {
        "lr": 1e-5,
        "d_x": 2, # input dimension
        "d_y": 1, # output dimension
        "batch_size": 1,
        "max_iters": 20,
        "iters_per_epoch":1
    }
    leap_fed_learn.hyperparams = hyperparams
    local_leap = leap.DistributedLeap(leap_fed_learn)
    local_leap.send_request()

def main():
    predef_count_exp()

if __name__ == "__main__":
    main()