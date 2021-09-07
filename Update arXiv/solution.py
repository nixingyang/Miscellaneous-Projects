import glob
import logging
import os

import arxiv
import requests
from absl import app, flags

flags.DEFINE_string("root_folder_path", "~/Downloads/Papers",
                    "Folder path of the root directory.")
FLAGS = flags.FLAGS


def format_title(title):
    title = title.replace(":", " ")
    title = title.replace("\n", " ")
    while "  " in title:
        title = title.replace("  ", " ")
    return title


def main(_):
    # Find the pdf files within root_folder_path
    root_folder_path = os.path.abspath(
        os.path.expanduser(FLAGS.root_folder_path))
    source_file_path_list = sorted(
        glob.glob(os.path.join(root_folder_path, "**/*.pdf"), recursive=True))
    get_relative_path = lambda path: path[len(root_folder_path) + 1:]

    # Disable the logger for arxiv.arxiv
    # https://stackoverflow.com/a/2267567
    logger = logging.getLogger("arxiv.arxiv")
    logger.propagate = False

    # Iterate over the pdf files
    for source_file_path in source_file_path_list:
        # Query with id_without_version
        id_without_version = os.path.basename(source_file_path).split(" ")[0]
        id_without_version = ".".join(id_without_version.split(".")[:2])
        id_without_version = id_without_version.split("v")[0]
        query_result_list = arxiv.query(id_list=[id_without_version])
        if not query_result_list:
            print("Failed to analyze {}.".format(
                get_relative_path(source_file_path)))
            continue

        # Update the pdf file if needed
        query_result = query_result_list[0]
        title = format_title(query_result["title"])
        pdf_url = query_result["pdf_url"]
        id_with_version = pdf_url.split("/")[-1]
        target_file_path = os.path.abspath(
            os.path.join(source_file_path, "..",
                         f"{id_with_version} {title}.pdf"))
        if os.path.isfile(target_file_path):
            if source_file_path != target_file_path:
                os.remove(source_file_path)
        else:
            print("Updating {} with {}".format(
                get_relative_path(source_file_path),
                get_relative_path(target_file_path)))
            open(target_file_path, "wb").write(requests.get(pdf_url).content)
            os.remove(source_file_path)

    print("All done!")


if __name__ == "__main__":
    app.run(main)
