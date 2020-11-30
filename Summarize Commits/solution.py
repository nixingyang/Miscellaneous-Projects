import calendar
import datetime
import os
import subprocess

import pandas as pd
from absl import app, flags

flags.DEFINE_string("root_folder_path",
                    os.path.expanduser("~/Documents/Local Storage/Source Code"),
                    "Path of the root folder.")
flags.DEFINE_list("skipped_folder_names", "Miscellaneous Projects,PhD",
                  "Skipped folder names.")
flags.DEFINE_string("author", "nixingyang", "Author.")
flags.DEFINE_string("start_date", "2020-03-01", "Start date.")
flags.DEFINE_string("end_date", "2020-06-30", "End date.")
flags.DEFINE_string(
    "holiday_dates",
    "2020-01-06 2020-04-10 2020-04-13 2020-05-01 2020-05-21 2020-06-19 2020-12-24 2020-12-25",
    "Holiday dates.")
flags.DEFINE_string("hours", "7,35", "Working hours.")
flags.DEFINE_string("dummy_task", "TBD", "Dummy value for the task.")
FLAGS = flags.FLAGS


def merge_commit_messages(commit_message_list,
                          skipped_keywords=["Merge", "Revert"],
                          max_commit_messages=5):
    # Remove duplicate entries, and sort them
    commit_message_list = sorted(set(commit_message_list))

    # Skip commit messages which start with certain keywords
    commit_message_list = [
        item for item in commit_message_list
        if sum([item.startswith(keyword) for keyword in skipped_keywords]) == 0
    ]

    commit_messages = []
    start_index = 0
    while start_index < len(commit_message_list):
        # Get current trunk
        entries = commit_message_list[start_index:start_index +
                                      max_commit_messages]

        # Merge entries
        commit_message = "; ".join(sorted(entries))

        # Replace ".;" with ";"
        commit_message = commit_message.replace(".;", ";")

        # Add entries
        commit_messages.append(commit_message)

        start_index += max_commit_messages

    return commit_messages


def main(_):
    # Get the folder path of all repositories
    repository_folder_path_list = []
    for item in sorted(os.listdir(FLAGS.root_folder_path)):
        repository_folder_path = os.path.join(FLAGS.root_folder_path, item)
        if os.path.isdir(repository_folder_path) and not os.path.basename(
                repository_folder_path) in FLAGS.skipped_folder_names:
            repository_folder_path_list.append(repository_folder_path)

    # Initialize datetime
    init_datetime = lambda input_date: datetime.datetime(
        *[int(item) for item in input_date.split("-")])
    start_datetime = init_datetime(FLAGS.start_date)
    end_datetime = init_datetime(FLAGS.end_date)
    holiday_datetime_list = [
        init_datetime(item) for item in FLAGS.holiday_dates.split(" ")
    ]

    data_frame = pd.DataFrame(columns=["Day", "Date", "Hours", "Task"])
    extra_commit_messages = []
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
        commit_messages = merge_commit_messages(commit_message_list)

        # Check whether it is a working day
        is_working_day = current_datetime.weekday(
        ) <= 4 and current_datetime not in holiday_datetime_list

        # Add record to the data frame
        if is_working_day:
            if len(commit_messages) == 0:
                commit_messages = [FLAGS.dummy_task]
            data_frame = data_frame.append(pd.Series([
                list(calendar.day_abbr)[current_datetime.weekday()],
                f"{current_datetime.day}.{current_datetime.month}.{current_datetime.year}",
                FLAGS.hours, commit_messages[0]
            ],
                                                     index=data_frame.columns),
                                           ignore_index=True)
            if len(commit_messages) > 1:
                extra_commit_messages += commit_messages[1:]
        elif len(commit_messages) > 0:
            extra_commit_messages += commit_messages

        # Get the next day
        # https://stackoverflow.com/a/3240486
        current_datetime += datetime.timedelta(days=1)

    # Fill in the records with dummy task
    dummy_task_indexes = data_frame.index[data_frame["Task"] ==
                                          FLAGS.dummy_task].tolist()
    for index, value in zip(dummy_task_indexes, extra_commit_messages):
        data_frame.loc[index, "Task"] = value

    # Save the Excel sheet
    assert data_frame["Task"].duplicated().sum() == 0
    with pd.ExcelWriter(f"{FLAGS.start_date} {FLAGS.end_date}.xlsx") as writer:  # pylint: disable=abstract-class-instantiated
        data_frame.to_excel(writer, index=False)

    # Save the remaining commit messages
    remaining_commit_messages = extra_commit_messages[len(dummy_task_indexes):]
    if len(remaining_commit_messages) > 0:
        with open(f"{FLAGS.start_date} {FLAGS.end_date}.txt",
                  "w") as file_object:
            for commit_message in remaining_commit_messages:
                file_object.write(f"{commit_message}\n")

    print("All done!")


if __name__ == "__main__":
    app.run(main)
