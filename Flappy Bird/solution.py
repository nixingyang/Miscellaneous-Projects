# https://github.com/keras-team/keras/issues/8429
import tensorflow as tf
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)
from keras import backend as K
K.set_session(session)

def run():
    print("All done!")

if __name__ == "__main__":
    run()