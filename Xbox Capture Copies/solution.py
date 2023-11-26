import argparse
import glob
import os

argument_parser = argparse.ArgumentParser()
argument_parser.add_argument("--source_folder_path", default="XboxCaptureCopies")
argument_parser.add_argument("--target_folder_path", default="Games")
arguments = argument_parser.parse_args()


def run():
    # Find the source files
    source_file_path_pattern = os.path.join(arguments.source_folder_path, "**/*.png")
    source_file_path_list = sorted(glob.glob(source_file_path_pattern, recursive=True))

    # Process the source files
    for source_file_path in source_file_path_list:
        source_file_name = os.path.basename(source_file_path)
        separator_index = source_file_name.find("-")
        title = source_file_name[:separator_index]
        timestamp = source_file_name[separator_index + 1 :]
        workspace_folder_path = os.path.join(arguments.target_folder_path, title)
        os.makedirs(workspace_folder_path, exist_ok=True)
        target_file_path = os.path.join(workspace_folder_path, timestamp)
        os.rename(source_file_path, target_file_path)

    print("All done!")


if __name__ == "__main__":
    run()
