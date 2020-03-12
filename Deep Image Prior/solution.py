import matplotlib
matplotlib.use("Agg")

import os
import cv2
import pylab
import numpy as np
from keras.callbacks import Callback, ModelCheckpoint

from load_model import init_model
from load_dataset import init_batch_generators

# Data
IMAGE_URL = "https://avatars.githubusercontent.com/u/15064790?s=460&v=4"
IMAGE_SIZE = (256, 256)
MEAN = 0
STANDARD_DEVIATION = 10

# Training
LEARNING_RATE = 0.0001
FILTERS_LIST = [32, 64, 128, 256, 512]
STEPS_PER_EPOCH = 100
EPOCHS = 1000000

# Output
OUTPUT_FOLDER_PATH = os.path.join("/tmp", __file__.split(os.sep)[-2])
OPTIMAL_WEIGHTS_FOLDER_PATH = os.path.join(OUTPUT_FOLDER_PATH,
                                           "optimal weights")
PREDICTIONS_FOLDER_PATH = os.path.join(OUTPUT_FOLDER_PATH, "predictions")


class InspectLoss(Callback):

    def __init__(self):
        super(InspectLoss, self).__init__()

        self.train_loss_list = []
        self.valid_loss_list = []

    def on_epoch_end(self, epoch, logs=None):
        train_loss = logs.get("loss")
        valid_loss = logs.get("val_loss")
        self.train_loss_list.append(train_loss)
        self.valid_loss_list.append(valid_loss)
        epoch_index_array = np.arange(len(self.train_loss_list)) + 1

        pylab.figure()
        pylab.plot(epoch_index_array,
                   self.train_loss_list,
                   "yellowgreen",
                   label="train_loss")
        pylab.plot(epoch_index_array,
                   self.valid_loss_list,
                   "lightskyblue",
                   label="valid_loss")
        pylab.grid()
        pylab.legend(bbox_to_anchor=(0., 1.02, 1., .102),
                     loc=2,
                     ncol=2,
                     mode="expand",
                     borderaxespad=0.)
        pylab.savefig(os.path.join(OUTPUT_FOLDER_PATH, "loss_curve.png"))
        pylab.close()


class InspectPredictions(Callback):

    def __init__(self, batch_generator):
        super(InspectPredictions, self).__init__()

        self.batch_generator = batch_generator

    def visualize_image_content(self, image_content_array, epoch, split_name):
        for image_index, image_content in enumerate(
            (image_content_array * 255).astype(np.uint8), start=1):
            image_file_path = os.path.join(
                PREDICTIONS_FOLDER_PATH,
                "epoch_{}_sample_{}_{}.png".format(epoch + 1, image_index,
                                                   split_name))
            cv2.imwrite(image_file_path, image_content)

    def on_epoch_end(self, epoch, logs=None):
        input_image_content_array, _ = next(self.batch_generator)
        predicted_image_content_array = self.model.predict_on_batch(
            input_image_content_array)

        self.visualize_image_content(predicted_image_content_array,
                                     epoch,
                                     split_name="prediction")


def run():
    print("Creating folders ...")
    for folder_path in [OPTIMAL_WEIGHTS_FOLDER_PATH, PREDICTIONS_FOLDER_PATH]:
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)
    print("Output folder is {}".format(OUTPUT_FOLDER_PATH))

    print("Initiating the model ...")
    model = init_model(IMAGE_SIZE, FILTERS_LIST, LEARNING_RATE,
                       os.path.join(OPTIMAL_WEIGHTS_FOLDER_PATH, "model.png"))

    print("Initiating the batch generators ...")
    train_batch_generator, valid_batch_generator, inspection_batch_generator = init_batch_generators(
        IMAGE_URL, IMAGE_SIZE, MEAN, STANDARD_DEVIATION, OUTPUT_FOLDER_PATH)

    print("Performing the training procedure ...")
    modelcheckpoint_callback = ModelCheckpoint(
        os.path.join(OPTIMAL_WEIGHTS_FOLDER_PATH, "model.h5"),
        monitor="val_loss",
        save_best_only=True,
        save_weights_only=False,
        verbose=1)  # NB: Theoretically,ground truth might be unavailable.
    inspectloss_callback = InspectLoss()
    inspectpredictions_callback = InspectPredictions(inspection_batch_generator)
    model.fit_generator(generator=train_batch_generator,
                        steps_per_epoch=STEPS_PER_EPOCH,
                        validation_data=valid_batch_generator,
                        validation_steps=1,
                        callbacks=[
                            modelcheckpoint_callback, inspectloss_callback,
                            inspectpredictions_callback
                        ],
                        epochs=EPOCHS,
                        verbose=2)

    print("All done!")


if __name__ == "__main__":
    run()
