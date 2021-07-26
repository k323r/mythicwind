import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.python.ops import math_ops
from matplotlib import pyplot as plt
from tensorflow.keras import Model
from tensorflow.keras.layers import Conv1D, Dense, Conv2D, Layer, Lambda
#from sklearn.preprocessing import StandardScaler
from tensorflow.keras.initializers import Initializer, Ones
from tensorflow.keras.callbacks import Callback, TensorBoard
from pathlib import Path
from tensorflow.keras import backend as K
import importlib
import utils as utl
from abc import abstractmethod, ABC

DTYPE = tf.float32

class NaivePast(Model):
    def __init__(self, naive_lag, quant_n, quant_range, deflection_channel, model_name = "NaivePast"):
        super(NaivePast, self).__init__(name = model_name)

        self.lag = naive_lag
        self.bins = list(np.linspace(quant_range[0], quant_range[1], quant_n + 1)[:-1])
        self.quant_n = quant_n
        self.deflection_channel = deflection_channel

    @property
    def max_lag(self):
        return self.lag

    def call(self, inp, training=False):
        inp_max = tf.nn.max_pool1d(inp[:,:,self.deflection_channel:self.deflection_channel+1], ksize = self.lag, strides = 1, padding = "VALID")
        inp_binned = math_ops._bucketize(inp_max, self.bins) - 1
        return tf.one_hot(tf.squeeze(inp_binned,axis = -1), depth = self.quant_n)

class NaiveConstant(Model):
    def __init__(self, class_pred, quant_n, model_name = "NaiveConstant"):
        super(NaiveConstant, self).__init__(name = model_name)

        self.class_pred = class_pred
        self.quant_n = quant_n

    @property
    def max_lag(self):
        return 1

    def call(self, inp, training=False):
        pred_ones = tf.ones_like(tf.reduce_min(inp, axis = -1, keepdims=True))
        pred_zeros = tf.zeros_like(tf.reduce_min(inp, axis = -1, keepdims=True))
        pred = []
        for k in range(self.quant_n):
            if k == self.class_pred:
                pred.append(pred_ones)
            else:
                pred.append(pred_zeros)
        return tf.concat(pred, axis = -1)

class TurbNet(Model):
    def __init__(self, ddc_hidden, ddc_filters, ddc_activation, quant_n, model_name = "TurbNet"):
        super(TurbNet, self).__init__(name = model_name)

        self.block_dconv = DDCBlock(ddc_hidden, ddc_filters, ddc_activation, quant_n)

    @property
    def max_lag(self):
        return np.power(2, self.block_dconv.hidden_layers)

    def call(self, inp, training=False):
        out = self.block_dconv(inp)
        return tf.nn.softmax(out[:, self.max_lag - 1:, :], axis=-1)

class DDCBlock(Layer):
    def __init__(self, hidden_layers, filters, activation, filters_out):
        super(DDCBlock, self).__init__()
        self.initializer = tf.keras.initializers.glorot_normal()
        self.activation = tf.keras.activations.get(activation)
        self.hidden_layers = hidden_layers
        self.filters = filters
        self.filters_out = filters_out

        self.layers = []
        for k in range(hidden_layers):
            if k == hidden_layers-1:
                filt = filters_out
            else:
                filt = filters
            self.layers.append(
                Conv1D(filters=filt, kernel_size=2, activation=self.activation,
                       padding="causal",
                       dilation_rate=int(np.power(2, k)), use_bias= True,
                       kernel_initializer=self.initializer,
                       bias_initializer=tf.keras.initializers.constant(value=0.0),
                       kernel_regularizer=None))

    def call(self, inp, training=False):
        time_horizons = [self.layers[0](inp)]
        for k in range(1, len(self.layers)):
            time_horizons.append(self.layers[k](time_horizons[-1]))
        return time_horizons[-1]


