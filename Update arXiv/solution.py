import glob
import os

from absl import app, flags

flags.DEFINE_string("root_folder_path", "~/Downloads/Papers",
                    "Folder path of the root directory.")
FLAGS = flags.FLAGS


def main(_):
    # Find the pdf files within root_folder_path
    root_folder_path = os.path.abspath(
        os.path.expanduser(FLAGS.root_folder_path))
    file_path_list = sorted(
        glob.glob(os.path.join(root_folder_path, "**/*.pdf"), recursive=True))

    print("All done!")


if __name__ == "__main__":
    app.run(main)
