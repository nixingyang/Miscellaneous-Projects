import calendar
import datetime
import os

import pandas as pd
from absl import app, flags

flags.DEFINE_string("root_folder_path",
                    os.path.expanduser("~/Documents/Local Storage/Source Code"),
                    "Path of the root folder.")
flags.DEFINE_list("skipped_folder_names", "Miscellaneous Projects,PhD",
                  "Skipped folder names.")
flags.DEFINE_string("author", "nixingyang", "Author.")
flags.DEFINE_string("start_date", "2020-12-01", "Start date.")
flags.DEFINE_string("end_date", "2020-12-31", "End date.")
flags.DEFINE_string(
    "holiday_dates",
    "2020-01-06 2020-04-10 2020-04-13 2020-05-01 2020-05-21 2020-06-19 2020-12-24 2020-12-25",
    "Holiday dates.")
flags.DEFINE_string("hours", "7,25", "Working hours.")
flags.DEFINE_string("dummy_task", "TBD", "Dummy value for the task.")
FLAGS = flags.FLAGS


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
        commit_messages = []

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
    extra_commit_messages = extra_commit_messages[len(dummy_task_indexes):]

    # Use longer commit message
    while True:
        if len(extra_commit_messages) == 0:
            break

        # Find the index of the min or max value
        data_frame_task_length_series = data_frame["Task"].map(lambda x: len(x))
        index_in_data_frame_task = data_frame_task_length_series.idxmin()
        value_in_data_frame_task = data_frame_task_length_series.loc[
            index_in_data_frame_task]
        extra_commit_message_length_list = [
            len(item) for item in extra_commit_messages
        ]
        value_in_extra_commit_message = max(extra_commit_message_length_list)
        index_in_extra_commit_message = extra_commit_message_length_list.index(
            value_in_extra_commit_message)
        if value_in_data_frame_task >= value_in_extra_commit_message:
            break

        # Swap values
        data_frame.loc[index_in_data_frame_task, "Task"], extra_commit_messages[
            index_in_extra_commit_message] = extra_commit_messages[
                index_in_extra_commit_message], data_frame.loc[
                    index_in_data_frame_task, "Task"]

    # Save the Excel sheet
    if data_frame["Task"].duplicated().sum() != 0:
        print("There are duplicated entries.")
    with pd.ExcelWriter(f"{FLAGS.start_date} {FLAGS.end_date}.xlsx") as writer:  # pylint: disable=abstract-class-instantiated
        data_frame.to_excel(writer, index=False)

    # Save the remaining unused commit messages
    if len(extra_commit_messages) > 0:
        with open(f"{FLAGS.start_date} {FLAGS.end_date}.txt",
                  "w") as file_object:
            for commit_message in extra_commit_messages:
                file_object.write(f"{commit_message}\n")

    print("All done!")


if __name__ == "__main__":
    app.run(main)
