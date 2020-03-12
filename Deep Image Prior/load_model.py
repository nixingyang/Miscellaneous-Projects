from keras.layers import Input, Activation, SpatialDropout2D
from keras.layers.convolutional import Conv2D, UpSampling2D
from keras.layers.normalization import BatchNormalization
from keras.models import Model
from keras.optimizers import Adam
from keras.utils import plot_model


def init_CNN_block(input_tensor,
                   filters,
                   kernel_size=3,
                   scale_factor=2,
                   dropout_rate=0.2,
                   activation="relu"):
    output_tensor = Conv2D(filters=filters,
                           kernel_size=kernel_size,
                           strides=scale_factor,
                           padding="same")(input_tensor)
    output_tensor = BatchNormalization()(output_tensor)
    output_tensor = Activation(activation)(output_tensor)
    output_tensor = SpatialDropout2D(dropout_rate)(output_tensor)
    return output_tensor


def init_deCNN_block(input_tensor,
                     filters,
                     kernel_size=3,
                     scale_factor=2,
                     dropout_rate=0.2,
                     activation="relu"):
    output_tensor = UpSampling2D(scale_factor)(input_tensor)
    output_tensor = Conv2D(filters=filters,
                           kernel_size=kernel_size,
                           padding="same")(output_tensor)
    if activation != "sigmoid":
        output_tensor = BatchNormalization()(output_tensor)
    output_tensor = Activation(activation)(output_tensor)
    if activation != "sigmoid":
        output_tensor = SpatialDropout2D(dropout_rate)(output_tensor)
    return output_tensor


def init_model(image_size, filters_list, learning_rate,
               model_structure_file_path):
    # Retrieve input and output image shape
    input_image_row_num, input_image_column_num = image_size
    input_image_channel_num, output_image_channel_num = 3, 3

    # Define the vanilla input tensor
    vanilla_input_tensor = Input(shape=(input_image_row_num,
                                        input_image_column_num,
                                        input_image_channel_num))

    # Get the output tensor from the encoder
    current_output_tensor = vanilla_input_tensor
    for layer_index, filters in enumerate(filters_list):
        current_output_tensor = init_CNN_block(current_output_tensor, filters)

    # Get the output tensor from the decoder
    for layer_index, filters in enumerate(filters_list[:-1][::-1] +
                                          [output_image_channel_num]):
        if layer_index != len(filters_list) - 1:
            current_output_tensor = init_deCNN_block(current_output_tensor,
                                                     filters)
        else:
            current_output_tensor = init_deCNN_block(current_output_tensor,
                                                     filters,
                                                     activation="sigmoid")

    # Build up model
    model = Model(vanilla_input_tensor, current_output_tensor)
    model.compile(loss="mse", optimizer=Adam(lr=learning_rate))
    model.summary()
    plot_model(model,
               to_file=model_structure_file_path,
               show_shapes=True,
               show_layer_names=True)

    return model
