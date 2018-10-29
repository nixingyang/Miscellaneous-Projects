# https://github.com/keras-team/keras/issues/8429
import tensorflow as tf
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)
from keras import backend as K
K.set_session(session)

import cv2
import numpy as np
from keras.layers import Input, Conv2D, Activation, BatchNormalization, MaxPooling2D, GlobalAveragePooling2D, Dropout, Dense
from keras.models import Model
from keras.utils import plot_model

import os
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, "../external_resources/game")))
from wrapped_flappy_bird import GameState  # @UnresolvedImport pylint: disable=import-error

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
    print("Initiating the model ...")
    model = init_model()

    print("Initiating the GameState ...")
    game_state_object = GameState()

    # Take "do nothing" action
    vanilla_image_content, _, is_crashed = game_state_object.frame_step(input_actions=[1, 0])
    processed_image_content = np.swapaxes(vanilla_image_content, 0, 1)
    processed_image_content = cv2.cvtColor(processed_image_content, cv2.COLOR_RGB2GRAY)
    processed_image_content = cv2.resize(processed_image_content, (FRAME_WIDTH, FRAME_HEIGHT))
    processed_image_content = processed_image_content.astype(np.float32) / 255
    accumulated_image_content = np.stack([processed_image_content] * ACCUMULATED_FRAME_NUM, axis=-1)
    accumulated_image_content = np.expand_dims(accumulated_image_content, axis=0)

    print("All done!")

if __name__ == "__main__":
    run()
