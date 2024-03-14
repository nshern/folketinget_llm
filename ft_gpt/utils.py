import os
import xml.etree.ElementTree as ET
from datetime import datetime

import tiktoken
from openai import OpenAI

from ft_gpt import constants, utils


def get_current_date():
    return datetime.now().isoformat().split("T")[0]


def extract_date_from_xml(file):
    res = []
    with open(file, "r") as f:
        xml_data = f.read()
    root = ET.fromstring(xml_data)

    dates = root.findall(".//DateOfSitting")
    res = dates[0].text

    return res


def convert_date(date_str):
    # Parse the date string to a datetime object
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    # Format the date as desired
    # %d for day, %B for full month name, %Y for year
    formatted_date = date_obj.strftime("%d. %B %Y")

    return formatted_date


def get_date(s: str):
    return s.split("_")[-2]


def get_dates_of_sittings(reverse=False):
    dates = []
    files = os.listdir(constants.DATA_DIR_TEXT)

    for file in files:
        if str(file.title()) == "Overblik.Txt":
            continue
        else:
            date_of_sitting = f"{utils.get_date(file)}"
            dates.append(date_of_sitting)

    date_objects = [datetime.strptime(date, "%Y-%m-%d") for date in dates]

    if reverse is True:
        date_objects.sort(reverse=True)
    else:
        date_objects.sort()

    sorted_dates = [datetime.strftime(date, "%Y-%m-%d") for date in date_objects]

    return sorted_dates


def get_token_amount(text):
    encoding = tiktoken.encoding_for_model("text-embedding-3-large")
    return len(encoding.encode(text))


# TODO: write summarization function: https://huggingface.co/docs/transformers/tasks/summarization
def summarize_text():
    pass


def split_text(text, max_length=8191):
    """
    Splits the text into chunks of a maximum length.
    If the text is shorter than the max_length, it returns the text as is.
    If the text is longer, it splits it into smaller chunks of equal length,
    ensuring each chunk is under the max_length.
    """
    # Check if the current text is under the maximum length
    if get_token_amount(text) <= max_length:
        return text

    # If the text is longer than the max_length, split it into two halves
    half_length = len(text) // 2
    first_half = text[:half_length]
    second_half = text[half_length:]

    # Recursively split the halves if they are still too long
    split_first_half = split_text(first_half, max_length)
    split_second_half = split_text(second_half, max_length)

    # If the result of the split is not a list, make it a list
    if not isinstance(split_first_half, list):
        split_first_half = [split_first_half]
    if not isinstance(split_second_half, list):
        split_second_half = [split_second_half]

    # Combine the lists from both halves and return
    return split_first_half + split_second_half
