import glob
import os


def run(folder_path="./", filename_extension=".jpg"):
    source_file_path_list = glob.glob(
        os.path.join(folder_path, f"WoWScrnShot*{filename_extension}")
    )
    for source_file_path in source_file_path_list:
        source_file_name = os.path.basename(source_file_path)
        _, part_1, part_2 = source_file_name.split(".")[0].split("_")
        target_file_name = "{}{}{}{}{}".format(
            part_1[4], part_1[5], part_1[:4], part_2, filename_extension
        )
        target_file_path = os.path.abspath(
            os.path.join(source_file_path, "..", target_file_name)
        )
        os.rename(source_file_path, target_file_path)


if __name__ == "__main__":
    run()
