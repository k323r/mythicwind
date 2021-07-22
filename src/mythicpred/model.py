import numpy as np
import pandas as pd
import tensorflow as tf
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

class TurbNet(Model):
    def __init__(self, ddc_hidden, ddc_filters, ddc_activation, quant_n):
        super(TurbNet, self).__init__()

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


