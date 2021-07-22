import mythicpred.model as mdl
from mythicpred.util import pass_dict, get_default_cfg
from mythicpred.data import prep_turbine, random_batch_generator
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import backend as K
from tensorflow.keras.callbacks import Callback, TensorBoard
from pathlib import Path
import matplotlib.pyplot as plt
import argparse
import json
import os
import numpy as np
import pandas as pd
import tensorflow as tf

# parse command line
parser = argparse.ArgumentParser()
parser.add_argument("cfg", default="config.in", nargs='?',
                    help="Base configuration file to use (e.g. config.in). Must be a JSON-file of a config-dict. Final config is a combination of defaults and parameters set in this file.")
args = parser.parse_args()

# load configuration
cfg = get_default_cfg()
if os.path.exists(args.cfg):
    with open(args.cfg) as f:
        cfg_in = json.load(f)
    for key in cfg_in:
        cfg[key] = cfg_in[key]

# create output folders and save configuration
save_path = Path(cfg["save_path"]).joinpath(cfg["name"])
save_path_tb =  save_path.joinpath("tb")
if not os.path.exists(save_path):
    os.makedirs(save_path)
with open(Path(save_path.joinpath("config.in")), 'w') as f:
    json.dump(cfg, f, indent=4)

# preprocess turbine
df_turb = prep_turbine(**pass_dict(prep_turbine, cfg))

# prepare labels
bins = np.linspace(cfg["quant_range"][0], cfg["quant_range"][1], cfg["quant_n"] + 1)[:-1]
deflection_quant= np.digitize(df_turb.def_max_future.to_numpy(),bins) -1
labels_one_hot = np.zeros((deflection_quant.size, cfg["quant_n"]))
labels_one_hot[np.arange(deflection_quant.size),deflection_quant] = 1
labels_one_hot = labels_one_hot[np.newaxis, :]

# prepare input
idx_test_split = df_turb.index.get_loc(pd.to_datetime(cfg["test_split"]), method='nearest')
idx_eval_split = df_turb.index.get_loc(pd.to_datetime(cfg["eval_split"]), method='nearest')

ts_in = df_turb[['deflection','xz_angle']].to_numpy()
scaler = MinMaxScaler()
scaler.fit(ts_in[:idx_test_split, ::])
ts_in = scaler.transform(ts_in)
ts_in = ts_in[np.newaxis, ::]

# plt.figure(figsize = [12,8])
# plt.plot(df_turb.index, df_turb.xz_angle, label = "xz_angle")
# plt.plot(df_turb.index, df_turb.deflection, label = "deflection")
# plt.plot(df_turb.index, df_turb.def_max_future, label = "def_max_future")
# plt.legend()
del df_turb

model_init = getattr(mdl, cfg["model_name"])
model = model_init(**pass_dict(model_init.__init__, cfg))


optimizer = tf.keras.optimizers.get(cfg["optimizer"])
K.set_value(optimizer.lr, cfg["learning_rate"])

channels_in = 2 + 2 * cfg["use_env"]
channels_out = cfg["quant_n"]

ds_fit = tf.data.Dataset.from_generator(
                random_batch_generator(ts_in[:, :idx_test_split, :], labels_one_hot[:, :idx_test_split, :], [0, idx_test_split], model.max_lag, **pass_dict(random_batch_generator, cfg)),
                (tf.float32, tf.float32), output_shapes=(
                    tf.TensorShape(
                        [cfg["batch_size"], model.max_lag + cfg["label_length"] - 1,
                         channels_in]),
                    tf.TensorShape(
                        [cfg["batch_size"], cfg["label_length"], channels_out])))

model.compile(optimizer=optimizer, loss=tf.losses.get(cfg["loss"]),metrics = [tf.metrics.get("binary_accuracy")])
model.run_eagerly = cfg["run_eagerly"]
callbacks = []
callbacks.append(TensorBoard(log_dir=save_path_tb, profile_batch=0))
history = model.fit(ds_fit, validation_data= (ts_in[:, idx_test_split-model.max_lag + 1:idx_eval_split, :], labels_one_hot[:, idx_test_split:idx_eval_split, :]), epochs=cfg["epochs"], verbose=cfg["verbose"],
                    callbacks=callbacks)
model.summary()
model.save(save_path)

# evaluate model
metrics = []
ts_train = ts_in[:, :idx_test_split, :]
ts_test = ts_in[:, idx_test_split-model.max_lag + 1:idx_eval_split, :]
ts_eval = ts_in[:, idx_eval_split-model.max_lag + 1:, :]


labels_train = labels_one_hot[:, model.max_lag - 1 :idx_test_split, :]
labels_test = labels_one_hot[:, idx_test_split :idx_eval_split, :]
labels_eval = labels_one_hot[:, idx_eval_split :, :]

metrics.append([*model.evaluate(ts_train, labels_train, verbose = 0), labels_train.shape[1], model.max_lag - 1,idx_test_split])
metrics.append([*model.evaluate(ts_test, labels_test, verbose = 0), labels_test.shape[1],idx_test_split,idx_eval_split])
metrics.append([*model.evaluate(ts_eval, labels_eval, verbose = 0), labels_eval.shape[1], idx_eval_split,ts_in.shape[1]])

df_metrics = pd.DataFrame(metrics, index=  ["train", "test", "eval"], columns = ["loss", "accuracy", "dataset_length", "idx_start", "idx_end"])
print(df_metrics)
df_metrics.to_csv(save_path.joinpath("metrics.csv"))

