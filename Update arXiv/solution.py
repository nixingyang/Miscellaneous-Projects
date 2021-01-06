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
    source_file_path_list = sorted(
        glob.glob(os.path.join(root_folder_path, "**/*.pdf"), recursive=True))

    # Iterate over the pdf files
    for source_file_path in source_file_path_list:
        # Query with id_without_version
        id_without_version = os.path.basename(source_file_path).split(" ")[0]
        id_without_version = ".".join(id_without_version.split(".")[:2])
        id_without_version = id_without_version.split("v")[0]
        query_result_list = arxiv.query(id_list=[id_without_version])
        if not query_result_list:
            continue

    print("All done!")


if __name__ == "__main__":
    app.run(main)
