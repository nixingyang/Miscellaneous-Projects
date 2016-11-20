import os
from shutil import copyfile
from PIL import Image

IMAGE_SIZE_LIMIT = 256 * 1024  # In bytes
IMAGE_RESOLUTION = (1366, 768)
SOURCE_IMAGE_PATH = "/run/media/nixingyang/Data Center/OneDrive/Pictures/Bing Gallery/20160913_Meteora.jpg"
TARGET_IMAGE_PATH = "/run/media/nixingyang/Windows/Windows/System32/oobe/info/backgrounds/backgroundDefault.jpg"

def backup_file(original_file_path):
    if os.path.isfile(original_file_path):
        delimiter_index = original_file_path.rfind(".")
        backup_original_file_path = original_file_path[:delimiter_index] + "_backup" + original_file_path[delimiter_index:]
        copyfile(original_file_path, backup_original_file_path)

def generate_suitable_image(image_path, image_size_limit=IMAGE_SIZE_LIMIT):
    def generate_image_with_specific_quality(image_content, quality):
        image_name = os.path.basename(image_path)
        delimiter_index = image_name.rfind(".")
        new_image_name = image_name[:delimiter_index] + "_quality_{}".format(quality) + image_name[delimiter_index:]
        new_image_path = os.path.join("/tmp", new_image_name)
        if not os.path.isfile(new_image_path):
            image_content.save(new_image_path, quality=quality)
        image_size = os.path.getsize(new_image_path)
        return new_image_path, image_size < image_size_limit

    assert os.path.isfile(image_path), "{} does not exist!".format(image_path)
    image_content = Image.open(image_path)
    image_content = image_content.resize(IMAGE_RESOLUTION, Image.ANTIALIAS)

    lower_quality_bound = 1
    higher_quality_bound = 100
    while True:
        print("Working on lower_quality_bound {} with higher_quality_bound {} ...".format(lower_quality_bound, higher_quality_bound))

        lower_quality_image_path, is_lower_quality_image_suitable = generate_image_with_specific_quality(image_content, lower_quality_bound)
        higher_quality_image_path, is_higher_quality_image_suitable = generate_image_with_specific_quality(image_content, higher_quality_bound)

        if not is_lower_quality_image_suitable:
            assert False, "The lower quality image {} violates the limit of image size!".format(lower_quality_image_path)

        if is_higher_quality_image_suitable:
            return higher_quality_image_path

        if higher_quality_bound - lower_quality_bound <= 3:
            return lower_quality_image_path

        mean_quality_bound = int((lower_quality_bound + higher_quality_bound) / 2)
        mean_quality_image_path, is_mean_quality_image_suitable = generate_image_with_specific_quality(image_content, mean_quality_bound)
        if is_mean_quality_image_suitable:
            lower_quality_bound = mean_quality_bound
        else:
            higher_quality_bound = mean_quality_bound

def run():
    # Backup target image
    backup_file(TARGET_IMAGE_PATH)

    # Generate a suitable image which does not violate the limit of image size
    suitable_image_path = generate_suitable_image(SOURCE_IMAGE_PATH)

    # Save the suitable image as the target image
    copyfile(suitable_image_path, TARGET_IMAGE_PATH)

    print("All done!")

if __name__ == "__main__":
    run()
