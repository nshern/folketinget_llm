from datetime import datetime
import os
from ft_gpt import constants, utils


def convert_date(date_str):
    # Parse the date string to a datetime object
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    # Format the date as desired
    # %d for day, %B for full month name, %Y for year
    formatted_date = date_obj.strftime("%d. %B %Y")

    return formatted_date


def get_date(s: str):
    return s.split("_")[-2]


def get_dates_of_sittings():
    dates = []
    files = os.listdir(constants.DATA_DIR)

    for file in files:
        if str(file.title()) == "Overblik.Txt":
            continue
        else:
            date_of_sitting = f"{utils.get_date(file)}"
            dates.append(date_of_sitting)
    # Convert string dates to datetime objects
    date_objects = [datetime.strptime(date, "%Y-%m-%d") for date in dates]

    # Sort the date objects
    date_objects.sort()

    # If you need them back in string format
    sorted_dates = [datetime.strftime(date, "%Y-%m-%d") for date in date_objects]

    res = []

    for i in sorted_dates:
        res.append(i)

    return sorted_dates
