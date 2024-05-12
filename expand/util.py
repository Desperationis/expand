import os
import math
import requests
import re
import humanize
from datetime import datetime, timedelta
from abc import ABC, abstractmethod


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

class CompatibilityProbe(ABC):

    @abstractmethod
    def get_error_message(self) -> str:
        pass

    @abstractmethod
    def is_compatible(self) -> bool:
        pass

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
    return set(links)


def is_url_up(url) -> bool:
    """
    Returns true if url returns 200 HTTP Status Code on HEAD.
    """
    try:
        response = requests.head(url, allow_redirects=True)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.ConnectionError:
        return False

