"""
Functions that help `expand` work.
"""

import os
import re
import logging
import requests
import humanize
from datetime import datetime, timedelta
from expand.probes import *


def timedelta_since_last_update(file_path: str):
    """
    Return datetime.timedelta of a file. Raise FileNotFoundError if file
    doesn't exist.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError

    # Get the last modification time of the file
    last_update_timestamp = os.path.getmtime(file_path)
    last_update_datetime = datetime.fromtimestamp(last_update_timestamp)

    # Calculate the time difference from now
    time_difference = datetime.now() - last_update_datetime

    return time_difference


def timedelta_pretty(time_difference: timedelta):
    """
    Return prettified version of a datetime.timedelta in the form:

    "x year(s) ago"
    "x months(s) ago"
    "x weeks(s) ago"
    "x days(s) ago"
    "x hours(s) ago"
    "x minutes(s) ago"
    """

    # I'm just going to have this library do the heavy lifting for me
    return humanize.naturaltime(time_difference)


def get_failing_probes(probes: list[CompatibilityProbe]) -> list[CompatibilityProbe]:
    """
    Run every probe in a list of `probes` and return the failing probes.
    """

    return list(filter(lambda probe: not probe.is_compatible(), probes))


def filter_str_for_urls(string) -> set[str]:
    """
    Search for urls in string via regex. Ignores whitespace.
    """

    links = re.findall(r"(https?://\S+)", string)
    links = [link.replace('"', "") for link in links]
    links = [link.replace("'", "") for link in links]
    links = [link.replace(")", "") for link in links]
    links = [link.replace("(", "") for link in links]
    return set(links)


def get_probes_from_file(file_path: str):
    """
    Given an ansible file, return the list of probes by parsing the first line.
    If the ansible file doesn't have a list, raise Exception.
    """

    with open(file_path, "r", encoding="UTF-8") as file:
        first_line = file.readline()
        if first_line.startswith("#"):
            # Literally run it as python code
            first_line = first_line[1:].strip()
            result = eval(first_line)

            logging.debug(result)

            return result

        raise LookupError(f"Probes not found in {file_path}")


def is_url_up(url) -> bool:
    """
    Returns true if url returns 200 HTTP Status Code on HEAD.
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def get_files(directory: str):
    """
    Shows the files in the immediate top level of a `directory`. This is what
    is returned:
    """
    files_dict = {}

    if not os.path.isdir(directory):
        raise ValueError(f"The directory '{directory}' does not exist.")

    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)
        if os.path.isfile(full_path):
            files_dict[filename] = full_path

    return files_dict


def get_ansible_description(file_content: str, max_length: int) -> list[str]:
    """
    Given the CONTENT (string form) of a ansible file specifically made for
    `expand`, extract its description. This is defined as all the consecutive
    comments after the probe comment.

    E.x. 
    # [probe1(), probe2(), ...]
    # This is the first line.
    # This is the second line.

    Each newline character creates a new line in the output. However, if a line
    is longer than `max_width`, it gets split into many lines that are
    `max_width` long.

    Each lines has all left whitespace removed, and whenever a line gets moved
    to another line, the word is wrapped around.

    If the file does not contain any description, return "N/A"
    """

    lines = file_content.split("\n")
    comments = []
    for line in lines:
        if line.startswith("#"):
            comments.append(line)
        else:
            break
    
    if len(comments) <= 1:
        return ["N/A"]

    # These lines are all descriptions without # or whitespace
    comments = list(map(lambda a: a.lstrip("# \t"), comments[1:]))

    def split_sentence(sentence, index):
        # Find the closest space before the index to split the sentence
        split_index = index
        while split_index > 0 and sentence[split_index] != ' ':
            split_index -= 1
        
        # If no space is found, split at the index directly
        if split_index == 0:
            split_index = index
        
        # Return the split sentence
        return [sentence[:split_index], sentence[split_index+1:]]


    result = []
    for string in comments:
        while len(string) > max_length:
            split = split_sentence(string, max_length)
            result.append(split[0])
            string = split[1]

        result.append(string)

    return result



def get_formatted_columns(
    data: list[str], width, sizes: list[int] | None = None
) -> list[tuple[str, int]]:
    """
    Given a list `data` and `width`, return a list of (str, int) such that
    whenever `str` is drawn from an offset x `int`, the data appears to be in
    columns. For example:

        data: ["data1", "data2", "data3", "data4"]
        width: 20

            -> [("data1", 0), ("data2", 5), ("data3", 10), ("data4", 15)]

        If drawn, the resulting string would look like:
            "data1data2data3data4"

        If the width was greater, it would look like:
            "data1  data2  data3  data4"

        The data gets truncated if width is too small:
            "dadadada"

        If width < len(data), return []
            ""

    You can also set columns to be a certain size. For example,
        size: [-1, 5, -1] sets the first and last column to the same size while the
        middle is 5.
    """

    def normalize_sizes(sizes: list[int], width):
        """
        Replaces any -1 in `sizes` with the same width to maximize content
        fitting in `width`.
        """
        fixed_entries = list(filter(lambda a: a > 0, sizes))
        if len(fixed_entries) == len(sizes):
            return sizes

        column_size = (width - sum(fixed_entries)) / (len(sizes) - len(fixed_entries))
        column_size = int(column_size)

        return list(map(lambda a: a if a > 0 else column_size, sizes))

    if width < len(data):
        return []
    if sizes is None:
        sizes = [-1] * len(data)
    if len(sizes) != len(data):
        raise RuntimeError("Sizes and data don't match up in size")

    sizes = normalize_sizes(sizes, width)

    output = []
    next_index = 0

    for i, col in enumerate(data):
        truncated = col[: sizes[i]]
        output.append((truncated, next_index))
        next_index += sizes[i]

    return output
