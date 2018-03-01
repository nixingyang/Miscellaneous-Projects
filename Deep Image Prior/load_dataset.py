import os
import cv2
import urllib
import numpy as np

def load_image(image_url, image_file_path):
    if not os.path.isfile(image_file_path):
        print("Downloading image from {} ...".format(image_url))
        urllib.urlretrieve(image_url, image_file_path)

    print("Loading image from {} ...".format(image_file_path))
    image_content = cv2.imread(image_file_path)
    return image_content

def get_corrupted_image_content(original_image_content, mean, standard_deviation):
    print("Adding noise with mean {} and standard_deviation {} ...".format(mean, standard_deviation))
    noise = np.random.normal(loc=mean, scale=standard_deviation, size=original_image_content.shape)
    corrupted_image_content = np.clip(original_image_content + noise, 0, 255).astype(np.uint8)
    return corrupted_image_content

def get_batch_generator(input_image_content_array, output_image_content_array):
    while True:
        yield input_image_content_array, output_image_content_array

def init_batch_generators(image_url, image_size, mean, standard_deviation, output_folder_path):
    vanilla_image_content = load_image(image_url, os.path.join(output_folder_path, "vanilla.jpg"))

    image_width, image_height = image_size
    original_image_content = cv2.resize(vanilla_image_content, (image_width, image_height))
    cv2.imwrite(os.path.join(output_folder_path, "original.png"), original_image_content)

    corrupted_image_content = get_corrupted_image_content(original_image_content, mean, standard_deviation)
    cv2.imwrite(os.path.join(output_folder_path, "corrupted.png"), corrupted_image_content)

    input_image_content_array = np.random.uniform(low=0.0, high=1.0, size=[1] + list(corrupted_image_content.shape)).astype(np.float32)
    output_image_content_array = np.array([corrupted_image_content], dtype=np.float32) / 255
    train_batch_generator = get_batch_generator(input_image_content_array, output_image_content_array)

    output_image_content_array = np.array([original_image_content], dtype=np.float32) / 255
    valid_batch_generator = get_batch_generator(input_image_content_array, output_image_content_array)

    inspection_batch_generator = get_batch_generator(input_image_content_array, output_image_content_array)

    return train_batch_generator, valid_batch_generator, inspection_batch_generator
