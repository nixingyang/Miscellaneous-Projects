import glob
import os

import arxiv
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

    # Iterate over the pdf files
    for file_path in file_path_list:
        # Query with id_without_version
        id_without_version = ".".join(
            os.path.basename(file_path).split(".")[:2]).split("v")[0]
        query_results = arxiv.query(id_list=[id_without_version])
        if not query_results:
            continue

    print("All done!")


if __name__ == "__main__":
    app.run(main)
