def pass_dict(func, dict):
    return {key: value for key, value in dict.items() if key in func.__code__.co_varnames}

def get_default_cfg():
    cfg = {}
    # paths
    cfg["name"] = "turbine-8" # name of experiment
    cfg["save_path"] = "/home/rafael/runs/turb/" # save path of results
    cfg["path_turb"] = "/home/rafael/data/turb/proc_josch/turbine-08/helihoist-1/tom/acc-vel-pos" # path of input data

    # data and preprocessing
    cfg["eigenfreq"] = 0.23 # eigenfrequency of turbine
    cfg["pred_horizon"] = "600s" # future time frame for which maximal deflection will be predicted
    cfg["quant_range"] = [0.0, 0.4]
    cfg["quant_n"] = 2
    cfg["test_split"] = "2019-10-15 12:00 UTC"
    cfg["eval_split"] = "2019-10-18 00:00 UTC"
    cfg["use_env"] = False # not yet implemented
    cfg["use_scaler"] = True

    # model
    cfg["model_name"] = "TurbNet" # class name of used model, "TurbNet" "NaiveConstant"

    # TurbNet
    cfg["ddc_hidden"] = 10 # number of dyadic dilated convolutional layers
    cfg["ddc_filters"] = 4 # number of filters per hidden layer
    cfg["ddc_activation"] = "relu"

    # NaiveConstant
    cfg["class_pred"] = 0

    # NaivePast
    cfg["naive_lag"] = 280
    cfg["deflection_channel"] = 0

    # optimization
    cfg["learning_rate"] = 1e-3
    cfg["optimizer"] = "Adam"
    cfg["loss"] = "categorical_crossentropy"
    cfg["batch_size"] = 10
    cfg["label_length"] = 32
    cfg["steps_per_epoch"] = 16
    cfg["epochs"] = 500

    # tensorflow
    cfg["run_eagerly"] = False
    cfg["verbose"] = 'auto'

    return cfg