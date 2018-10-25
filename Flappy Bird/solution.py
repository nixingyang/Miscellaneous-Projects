# https://github.com/keras-team/keras/issues/8429
import tensorflow as tf
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)
from keras import backend as K
K.set_session(session)

import numpy as np
from keras.layers import Input, Conv2D, Activation, BatchNormalization, MaxPooling2D, GlobalAveragePooling2D, Dropout, Dense
from keras.models import Model
from keras.utils import plot_model

# Properties of frames
FRAME_HEIGHT, FRAME_WIDTH = 100, 60
ACCUMULATED_FRAME_NUM = 5

def init_model():
    # Define the input tensor
    input_tensor = Input((FRAME_HEIGHT, FRAME_WIDTH, ACCUMULATED_FRAME_NUM))

    # Get the output tensor
    output_tensor = input_tensor
    for block_index in np.arange(3) + 1:
        if block_index != 1:
            output_tensor = MaxPooling2D()(output_tensor)
        output_tensor = Conv2D(filters=32 * block_index, kernel_size=5, dilation_rate=2 ** (block_index - 1), padding="same")(output_tensor)
        output_tensor = Activation("relu")(output_tensor)
        output_tensor = BatchNormalization()(output_tensor)
    output_tensor = GlobalAveragePooling2D()(output_tensor)
    output_tensor = Dropout(rate=0.2)(output_tensor)
    output_tensor = Dense(2)(output_tensor)

    # Define the model
    model = Model(input_tensor, output_tensor)
    model.summary()
    plot_model(model, to_file="/tmp/model.png", show_shapes=True, show_layer_names=True)
    return model

def run():
    model = init_model()
    print("All done!")

if __name__ == "__main__":
    run()