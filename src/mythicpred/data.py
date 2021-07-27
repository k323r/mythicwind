import pandas as pd
import numpy as np
from mythicpred.util import pass_dict
import matplotlib.pyplot as plt
from mythicwind.csv_io import read_frame, read_frames_parallel
import tensorflow as tf

def prep_turbine(path_turb, eigenfreq = 0.23, pred_horizon = "600s", path_env = None):
    # load turbine data
    df_turb = pd.concat(read_frames_parallel(path_turb))[["pos_x", "pos_z", "deflection"]]

    # compute maximum future deflection time series
    df_turb["def_max_future"] = df_turb["deflection"][::-1].rolling(window=pred_horizon).max()[::-1]

    # subsample
    window = f'{int(1000.0/(eigenfreq*2))}ms'
    df_turb_sub = df_turb.abs().resample(window).max().interpolate()

    del df_turb

    def f_atan(x ,y):
        a = np.math.atan2(x, y)
        return np.min([np.math.pi/2.0 - a, a])

    df_turb_sub["xz_angle"] = df_turb_sub.apply(lambda x: f_atan(x.pos_x, x.pos_z), axis = 1)
    return df_turb_sub[["deflection", "xz_angle", "def_max_future"]]

def random_batch_generator(ts_in, ts_labels, idx_range_train, max_lag, label_length, batch_size, steps_per_epoch):
    def generator(training=False):
        for k in range(steps_per_epoch):
            x = []
            y = []
            for k2 in range(batch_size):
                idx = np.random.randint(idx_range_train[0] + max_lag, idx_range_train[1] - label_length)
                x.append(ts_in[:, idx - max_lag:idx + label_length - 1, :])
                y.append(ts_labels[:,idx:idx + label_length,:])
            x = tf.concat(x, axis=0)
            y = tf.concat(y, axis=0)
            yield x, y
    return generator

if __name__ == '__main__':
    cfg = {}
    cfg["eigenfreq"] = 0.23
    cfg["path_turb"] = "/home/rafael/data/turb/proc_josch/turbine-08/helihoist-1/tom/acc-vel-pos"
    cfg["pred_horizon"] = "600s"
    df_turb = prep_turbine(**pass_dict(prep_turbine, cfg))
    plt.figure(figsize = [12,8])
    plt.plot(df_turb.index, df_turb.xz_angle, label = "xz_angle")
    plt.plot(df_turb.index, df_turb.deflection, label = "deflection")
    plt.plot(df_turb.index, df_turb.def_max_future, label = "def_max_future")
    plt.legend()
    print(np.sum(df_turb.def_max_future < 0.2)/len(df_turb))
    #df_turb.plot(figsize=[12,4])
    plt.show()

