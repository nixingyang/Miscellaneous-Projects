import os

from absl import app, flags

flags.DEFINE_string("root_folder_path",
                    os.path.expanduser("~/Documents/Local Storage/Source Code"),
                    "Path of the root folder.")
flags.DEFINE_string("author", "nixingyang", "Author.")
flags.DEFINE_string("start_date", "2020-03-01", "Start date.")
flags.DEFINE_string("end_date", "2020-06-30", "End date.")
flags.DEFINE_string("hours", "7,35", "Working hours.")
FLAGS = flags.FLAGS


def main(_):
    # Get the folder path of all repositories
    repository_folder_path_list = []
    for item in sorted(os.listdir(FLAGS.root_folder_path)):
        repository_folder_path = os.path.join(FLAGS.root_folder_path, item)
        if os.path.isdir(repository_folder_path):
            repository_folder_path_list.append(repository_folder_path)

    print("All done!")


if __name__ == "__main__":
    app.run(main)
