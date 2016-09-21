import pylab
import numpy as np

from keras.callbacks import TensorBoard
from keras.layers.core import Dense
from keras.layers.recurrent import LSTM
from keras.layers.wrappers import TimeDistributed
from keras.models import Sequential
from sklearn.cross_validation import StratifiedShuffleSplit
from sklearn.preprocessing import LabelBinarizer

SAMPLE_NUM = 5000
TIMESTAMP_NUM = 20
FEATURE_DIM = 32
LSTM_OUTPUT_DIM = 256
BATCH_SIZE = 64
MAXIMUM_EPOCH_NUM = 100

def load_data():
    # Generate data
    cluster_center_array = np.array([[0.5, 0.5], [-0.5, 0.5], [-0.5, -0.5], [0.5, -0.5]])
    covariance_matrix = np.array([[0.05, 0], [0, 0.05]])

    unique_instance_num = 6000
    unique_instance_num_from_one_label = int(unique_instance_num / len(cluster_center_array))
    unique_instance_num_from_one_label_in_one_cluster = int(unique_instance_num_from_one_label / (len(cluster_center_array) - 1))

    label_to_unique_instance = {}
    for label_index, label_value in enumerate(np.arange(len(cluster_center_array))):
        unique_instance_list = []

        for cluster_index, cluster_center in enumerate(cluster_center_array):
            if label_index == cluster_index:
                continue

            unique_instance_list.append(np.random.multivariate_normal(cluster_center, covariance_matrix, unique_instance_num_from_one_label_in_one_cluster))

        label_to_unique_instance[label_value] = np.vstack(unique_instance_list)

    # Visualization
    pylab.figure()
    for label_value, unique_instance_array in label_to_unique_instance.items():
        pylab.plot(unique_instance_array[:, 0], unique_instance_array[:, 1], ".", label=label_value)
    pylab.grid()
    pylab.axis("equal")
    pylab.legend(bbox_to_anchor=(0., 1.02, 1., .102),
                 loc=len(cluster_center_array),
                 ncol=len(cluster_center_array),
                 mode="expand", borderaxespad=0.)
    pylab.savefig("data_distribution.png")

    return label_to_unique_instance

def preprocess_data(label_to_unique_instance):
    instance_num = SAMPLE_NUM * TIMESTAMP_NUM
    instance_num_from_one_label = int(instance_num / len(label_to_unique_instance))

    X_list = []
    Y_list = []
    for label_value, unique_instance_array in label_to_unique_instance.items():
        single_X_array = unique_instance_array[np.random.choice(len(unique_instance_array), instance_num_from_one_label)]
        single_X_array = single_X_array.reshape((-1, TIMESTAMP_NUM, single_X_array.shape[-1]))
        single_Y_array = np.ones(len(single_X_array)) * label_value

        X_list.append(single_X_array)
        Y_list.append(single_Y_array)

    return np.vstack(X_list).astype(np.float32), np.hstack(Y_list).astype(np.int32)

def init_model(raw_feature_dim, unique_lable_num):
    model = Sequential()
    model.add(TimeDistributed(Dense(FEATURE_DIM, activation="relu"), input_shape=(TIMESTAMP_NUM, raw_feature_dim)))
    model.add(LSTM(LSTM_OUTPUT_DIM, activation="tanh", return_sequences=False))
    model.add(Dense(unique_lable_num, activation="softmax"))
    model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

    return model

def run():
    # Load and preprocess data
    label_to_unique_instance = load_data()
    X, Y = preprocess_data(label_to_unique_instance)

    # Encode labels
    label_binarizer = LabelBinarizer()
    transformed_Y = label_binarizer.fit_transform(Y)

    # Cross validation
    cross_validation_iterator = StratifiedShuffleSplit(Y, n_iter=1, test_size=0.4, random_state=0)
    for train_index, test_index in cross_validation_iterator:
        break

    # Init model
    model = init_model(raw_feature_dim=X.shape[-1], unique_lable_num=len(label_binarizer.classes_))

    # Training procedure
    model.fit(X[train_index], transformed_Y[train_index],
              batch_size=BATCH_SIZE, nb_epoch=MAXIMUM_EPOCH_NUM,
              validation_data=(X[test_index], transformed_Y[test_index]),
              callbacks=[TensorBoard(log_dir="/tmp/Sequence Classification")],
              verbose=2)

    print("All done!")

if __name__ == "__main__":
    run()
