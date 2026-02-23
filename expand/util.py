"""
Functions that help `expand` work.
"""

import os
import re
import pwd
import requests
from typing import Optional
from expand.probes import *


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



def get_formatted_columns(
    data: list[str], width, sizes: Optional[list[int]] = None
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

def strip_ansi(text: str) -> str:
    """
    Remove ANSI escape sequences from text.
    """
    return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)


def filter_choices(names: list[str], query: str) -> list[int]:
    """
    Return indices of `names` where `query` is a case-insensitive substring.
    Empty query returns all indices.
    """
    if not query:
        return list(range(len(names)))
    lower_query = query.lower()
    return [i for i, name in enumerate(names) if lower_query in name.lower()]


def change_user(username, euid=0):
    """
    Effectively change the user running this program by changing the UID, GUID,
    and environmental variables. For extra safety, you can optionally set EUID
    to another value as well.
    """

    # Get the user information from the username
    user_info = pwd.getpwnam(username)
    uid = user_info.pw_uid
    gid = user_info.pw_gid
    home_dir = user_info.pw_dir
    user_name = user_info.pw_name

    os.setregid(gid, gid)
    os.setreuid(uid, euid) 
    
    # Update environment variables
    os.environ['HOME'] = home_dir
    os.environ['USER'] = user_name
    os.environ['LOGNAME'] = user_name
    os.environ['SHELL'] = user_info.pw_shell

