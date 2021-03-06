# An algorithm that trains a model using federated learning.

import json
import pandas as pd
import torch
import torch.utils.data

class AverageMeter(object):
    """Computes and stores the average and current value"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

def map_fns():
    # Expects model, dataloader, optimizer, criterion to be predefined
    def map_fn1(data, state):
        dataloader = get_dataloader(hyperparams, data)
        if 'loss_history' in state:
            print("loss: {}".format(state["loss_history"][-1]))

        # Update model with new weights
        if 'model_weights' in state:
            model_weights = state["model_weights"]
            for i, (name, params) in enumerate(model.named_parameters()):
                params.data = torch.tensor(model_weights[i])
        # Accumulate gradients
        loss_meter = AverageMeter()
        for i, (X, Y) in enumerate(dataloader):
            X = X.float()
            Y = Y.float()
            output = model(X)
            loss = criterion(output, Y)
            loss_meter.update(loss.item())
            loss.backward()
            if i == hyperparams["iters_per_epoch"]:
                break
        # Store gradient as list
        client_grad = []
        for name, params in model.named_parameters():
            if params.requires_grad:
                client_grad.append(params.grad.cpu().tolist())

        result = {
            "grads": client_grad,
            "loss": loss_meter.avg
        }
        result = json.dumps(result)
        return result

    return [map_fn1]

def agg_fns():
    def agg_fn1(map_results):
        first_result = json.loads(map_results[0])
        agg_grad = first_result['grads']
        loss_meter = AverageMeter()
        loss_meter.update(first_result['loss'])

        for i in range(1,len(map_results)):
            map_result = json.loads(map_results[i])
            grad_result = map_result['grads']
            for j in range(len(agg_grad)):
                agg_grad[j] += grad_result[j]
            loss_meter.update(map_result['loss'])

        result = {
            "grad":agg_grad,
            "loss":loss_meter.avg
        }
        return result

    return [agg_fn1]

def update_fns():
    # Expects model and optimizer in global state
    def update_fn1(agg_result, state):
        state["i"] += 1
        if "loss_history" in state:
            state["loss_history"].append(agg_result["loss"])
        else:
            state["loss_history"] = [agg_result["loss"]]

        # update model weights
        # model = state["model"]
        # optimizer = state["optimizer"]
        agg_grad = agg_result["grad"]
        for i, (name, params) in enumerate(model.named_parameters()):
            if params.requires_grad:
                params.grad = torch.tensor(agg_grad[i])
            optimizer.step()
            optimizer.zero_grad()
        model_weights = []
        for name, params in model.named_parameters():
            model_weights.append(params.cpu().tolist())

        state["model_weights"] = model_weights
        return state

    return [update_fn1]

# Returns which map/agg fn to run
def choice_fn(state):
    return 0

# Formats the raw data into data usable by map_fn
# ex: Converting types, extracting rows/columns
def dataprep_fn(data):
    data = pd.DataFrame(data)
    X = data[["age", "bmi"]].astype('float').to_numpy()
    Y = data["grade"].astype('long').to_numpy()
    return X, Y

def stop_fn(agg_result, state):
    return state["i"] == hyperparams["max_iters"]

def postprocessing_fn(agg_result, state):
    return agg_result

def init_state_fn():
    state = {
        "i": 0,
    }
    return state
