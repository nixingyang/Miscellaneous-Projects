import calendar
import datetime

import pandas as pd
from absl import app, flags

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
    # Initialize datetime
    init_datetime = lambda input_date: datetime.datetime(
        *[int(item) for item in input_date.split("-")])
    start_datetime = init_datetime(FLAGS.start_date)
    end_datetime = init_datetime(FLAGS.end_date)
    holiday_datetime_list = [
        init_datetime(item) for item in FLAGS.holiday_dates.split(" ")
    ]

    data_frame = pd.DataFrame(columns=["Day", "Date", "Hours", "Task"])
    current_datetime = start_datetime
    while current_datetime <= end_datetime:
        # Check whether it is a working day
        is_working_day = current_datetime.weekday(
        ) <= 4 and current_datetime not in holiday_datetime_list

        # Add record to the data frame
        if is_working_day:
            data_frame = data_frame.append(pd.Series([
                list(calendar.day_abbr)[current_datetime.weekday()],
                f"{current_datetime.day}.{current_datetime.month}.{current_datetime.year}",
                FLAGS.hours, FLAGS.dummy_task
            ],
                                                     index=data_frame.columns),
                                           ignore_index=True)

        # Get the next day
        # https://stackoverflow.com/a/3240486
        current_datetime += datetime.timedelta(days=1)

    # Save the Excel sheet
    with pd.ExcelWriter(f"{FLAGS.start_date} {FLAGS.end_date}.xlsx") as writer:  # pylint: disable=abstract-class-instantiated
        data_frame.to_excel(writer, index=False)

    print("All done!")


if __name__ == "__main__":
    app.run(main)
