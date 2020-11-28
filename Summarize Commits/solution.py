import datetime
import os
import subprocess

from absl import app, flags

flags.DEFINE_string("root_folder_path",
                    os.path.expanduser("~/Documents/Local Storage/Source Code"),
                    "Path of the root folder.")
flags.DEFINE_string("author", "nixingyang", "Author.")
flags.DEFINE_string("start_date", "2020-03-01", "Start date.")
flags.DEFINE_string("end_date", "2020-06-30", "End date.")
flags.DEFINE_string(
    "holiday_dates",
    "2020-01-06 2020-04-10 2020-04-13 2020-05-01 2020-05-21 2020-06-19 2020-12-24 2020-12-25",
    "Holiday dates.")
flags.DEFINE_string("hours", "7,35", "Working hours.")
FLAGS = flags.FLAGS


def main(_):
    # Get the folder path of all repositories
    repository_folder_path_list = []
    for item in sorted(os.listdir(FLAGS.root_folder_path)):
        repository_folder_path = os.path.join(FLAGS.root_folder_path, item)
        if os.path.isdir(repository_folder_path):
            repository_folder_path_list.append(repository_folder_path)

    # Initialize datetime
    init_datetime = lambda input_date: datetime.datetime(
        *[int(item) for item in input_date.split("-")])
    start_datetime = init_datetime(FLAGS.start_date)
    end_datetime = init_datetime(FLAGS.end_date)
    holiday_datetime_list = [
        init_datetime(item) for item in FLAGS.holiday_dates.split(" ")
    ]

    current_datetime = start_datetime
    while current_datetime <= end_datetime:
        date = f"{current_datetime.year}-{current_datetime.month}-{current_datetime.day}"
        commit_message_list = []
        for repository_folder_path in repository_folder_path_list:
            # Retrieve commit messages
            command = f"cd \"{repository_folder_path}\"; git log --pretty=format:\"%s\" --all --author=nixingyang --after=\"{date} 00:00\" --before=\"{date} 23:59\""
            output = subprocess.check_output(command, shell=True, text=True)
            if len(output) > 0:
                commit_message_list += output.split("\n")

        # Get the next day
        # https://stackoverflow.com/a/3240486
        current_datetime += datetime.timedelta(days=1)

    print("All done!")


if __name__ == "__main__":
    app.run(main)
