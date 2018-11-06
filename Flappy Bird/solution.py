# https://github.com/keras-team/keras/issues/8429
import tensorflow as tf
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)
from keras import backend as K
K.set_session(session)

import matplotlib
matplotlib.use("Agg")

import cv2
import numpy as np
from collections import deque
from keras.layers import Input, Conv2D, Activation, GlobalAveragePooling2D, Dense
from keras.models import Model
from keras.optimizers import Adam
from keras.utils import plot_model

import os
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, "../external_resources/game")))
from wrapped_flappy_bird import GameState  # @UnresolvedImport pylint: disable=import-error

# Properties of frames
FRAME_HEIGHT, FRAME_WIDTH = 100, 60
ACCUMULATED_FRAME_NUM = 5

# Hyperparameters
GAMMA = 0.99
INITIAL_EPSILON, FINAL_EPSILON = 0.1, 0.0001
OBSERVE_STEP_NUM, EXPLORE_STEP_NUM, TRAIN_STEP_NUM = int(1e4), int(1e6), np.inf
SAMPLE_CONTAINER_MAX_LENGTH = int(1e5)
BATCH_SIZE = 32
LEARNING_RATE = 0.0001

# Output
OUTPUT_FOLDER_PATH = os.path.abspath(os.path.join(__file__, ".."))
MODEL_STRUCTURE_FILE_PATH = os.path.join(OUTPUT_FOLDER_PATH, "model.png")
MODEL_WEIGHTS_FILE_PATH = os.path.join(OUTPUT_FOLDER_PATH, "model.h5")
PREDICTION_FILE_PATH = os.path.join(OUTPUT_FOLDER_PATH, "prediction.mkv")

def init_model():
    # Define the input tensor
    input_tensor = Input((FRAME_HEIGHT, FRAME_WIDTH, ACCUMULATED_FRAME_NUM))

    # Get the output tensor
    output_tensor = input_tensor
    for block_index in np.arange(4) + 1:
        output_tensor = Conv2D(filters=64 * block_index, kernel_size=5, strides=2, padding="same")(output_tensor)
        output_tensor = Activation("relu")(output_tensor)
    output_tensor = GlobalAveragePooling2D()(output_tensor)
    output_tensor = Dense(2)(output_tensor)

    # Define the model
    model = Model(input_tensor, output_tensor)
    model.compile(loss="mean_squared_error", optimizer=Adam(lr=LEARNING_RATE))
    model.summary()
    plot_model(model, to_file=MODEL_STRUCTURE_FILE_PATH, show_shapes=True, show_layer_names=True)
    return model

def process_vanilla_image_content(vanilla_image_content):
    processed_image_content = cv2.cvtColor(vanilla_image_content, cv2.COLOR_RGB2GRAY)
    processed_image_content = cv2.resize(processed_image_content, (FRAME_WIDTH, FRAME_HEIGHT))
    processed_image_content = processed_image_content.astype(np.float32) / 255
    return processed_image_content

def run():
    print("Outputs will be saved to {} ...".format(OUTPUT_FOLDER_PATH))
    if not os.path.isdir(OUTPUT_FOLDER_PATH):
        os.makedirs(OUTPUT_FOLDER_PATH)

    print("Initiating the model ...")
    model = init_model()

    print("Initiating the GameState ...")
    game_state_object = GameState()

    print("Initiating the sample container ...")
    sample_container = deque([], maxlen=SAMPLE_CONTAINER_MAX_LENGTH)

    # Take "do nothing" action at the beginning
    vanilla_image_content, _, _ = game_state_object.frame_step(input_actions=[1, 0])

    # Get a dummy accumulated_image_content_before
    processed_image_content = process_vanilla_image_content(vanilla_image_content)
    accumulated_image_content_before = np.stack([processed_image_content] * ACCUMULATED_FRAME_NUM, axis=-1)
    accumulated_image_content_before = np.expand_dims(accumulated_image_content_before, axis=0)

    step_index = 0
    best_score = np.NINF
    vanilla_image_content_list = []
    while True:
        step_index += 1
        perform_training = True
        if step_index <= OBSERVE_STEP_NUM:
            print("observe {}/{}".format(step_index, OBSERVE_STEP_NUM))
            epsilon = INITIAL_EPSILON
            perform_training = False
        elif step_index <= OBSERVE_STEP_NUM + EXPLORE_STEP_NUM:
            print("explore {}/{}".format(step_index - OBSERVE_STEP_NUM, EXPLORE_STEP_NUM))
            epsilon = FINAL_EPSILON + 1.0 * (OBSERVE_STEP_NUM + EXPLORE_STEP_NUM - step_index) / EXPLORE_STEP_NUM * (INITIAL_EPSILON - FINAL_EPSILON)
        elif step_index <= OBSERVE_STEP_NUM + EXPLORE_STEP_NUM + TRAIN_STEP_NUM:
            print("train {}/{}".format(step_index - OBSERVE_STEP_NUM - EXPLORE_STEP_NUM, TRAIN_STEP_NUM))
            epsilon = FINAL_EPSILON
        else:
            break

        # Get the action_index either randomly or using predictions of the model
        input_actions = [0, 0]
        if np.random.random() < epsilon:
            action_index = np.random.choice(2)
        else:
            action_index = np.argmax(model.predict_on_batch(accumulated_image_content_before)[0])
        input_actions[action_index] = 1

        # Take actions
        vanilla_image_content, reward, is_crashed = game_state_object.frame_step(input_actions=input_actions)
        vanilla_image_content_list.append(vanilla_image_content)

        # Save the model if necessary
        if is_crashed:
            current_score = game_state_object.get_score()
            if current_score > best_score:
                print("Best score improved from {} to {} ...".format(best_score, current_score))
                best_score = current_score

                print("Saving model to {} ...".format(MODEL_WEIGHTS_FILE_PATH))
                model.save(filepath=MODEL_WEIGHTS_FILE_PATH, overwrite=True, include_optimizer=True)

                print("Saving prediction to {} ...".format(PREDICTION_FILE_PATH))
                videowriter_object = cv2.VideoWriter(PREDICTION_FILE_PATH, cv2.VideoWriter_fourcc(*"X264"), 20.0, vanilla_image_content.shape[:-1][::-1])
                for image_content in vanilla_image_content_list:
                    image_content = cv2.cvtColor(image_content, cv2.COLOR_RGB2BGR)
                    videowriter_object.write(image_content)
                videowriter_object.release()
                vanilla_image_content_list = []

        # Get accumulated_image_content_after and append observation
        processed_image_content = process_vanilla_image_content(vanilla_image_content)
        accumulated_image_content_after = np.append(accumulated_image_content_before[:, :, :, 1:], np.expand_dims(np.expand_dims(processed_image_content, axis=-1), axis=0), axis=-1)
        sample = (accumulated_image_content_before, action_index, accumulated_image_content_after, reward, is_crashed)
        sample_container.append(sample)

        # Perform training
        if perform_training:
            chosen_sample_list = [sample_container[index] for index in np.random.choice(len(sample_container), size=BATCH_SIZE)]
            accumulated_image_content_before_tuple, action_index_tuple, accumulated_image_content_after_tuple, reward_tuple, is_crashed_tuple = zip(*chosen_sample_list)
            accumulated_image_content_before_array = np.concatenate(accumulated_image_content_before_tuple)
            accumulated_image_content_after_array = np.concatenate(accumulated_image_content_after_tuple)

            reward_for_accumulated_image_content_before_array = model.predict_on_batch(accumulated_image_content_before_array)
            reward_for_accumulated_image_content_after_array = model.predict_on_batch(accumulated_image_content_after_array)
            reward_offset = GAMMA * np.max(reward_for_accumulated_image_content_after_array, axis=1) * np.invert(is_crashed_tuple)
            reward_for_accumulated_image_content_before_array[:, action_index_tuple] = reward_tuple + reward_offset

            train_loss = model.train_on_batch(accumulated_image_content_before_array, reward_for_accumulated_image_content_before_array)
            print("train_loss: {:.5f}".format(train_loss))

        # Update accumulated_image_content_before with accumulated_image_content_after
        accumulated_image_content_before = accumulated_image_content_after

    print("All done!")

if __name__ == "__main__":
    run()
