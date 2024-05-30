import os
import json

class InstalledCache:
    @staticmethod
    def _get_json():
        if not os.path.exists("installed.json"):
            return {}

        with open("installed.json", "r", encoding="UTF-8") as file:
            return json.load(file)


    @staticmethod
    def _get_attr(attr):
        data = InstalledCache._get_json()
        return data[attr]

    @staticmethod
    def _write_attr(attr, value):
        data = InstalledCache._get_json()

        with open("installed.json", "w+", encoding="UTF-8") as file:
            data[attr] = value
            file.write(json.dumps(data, sort_keys=True, indent=4))


    @staticmethod
    def is_installed(name):
        try:
            return InstalledCache._get_attr(name) == "installed"
        except:
            return False


    @staticmethod
    def is_failure(name):
        try:
            return InstalledCache._get_attr(name) == "failure"
        except:
            return False

    @staticmethod
    def set_installed(ansible_name):
        InstalledCache._write_attr(ansible_name, "installed")

    @staticmethod
    def set_failure(ansible_name):
        InstalledCache._write_attr(ansible_name, "failure")

