import os
import json

class InstalledCache:
    """
    The format for the cache file (installed.json) is as follows:

        {
            "OnlyRoot": {
                "package.yaml": "installed", 
                "package2.yaml": "failure",
                ...
            }

            "AnyUser": {
                "root": {
                    "localpackage1": "installed",
                    "localpackage2": "failure",
                    "localpackage3": "installed",
                }
                "user": {
                    "localpackage2": "installed",
                    ...
                }
            }
        }
    """
        

    @staticmethod
    def _get_json():
        if not os.path.exists("installed.json"):
            return {}

        with open("installed.json", "r", encoding="UTF-8") as file:
            return json.load(file)

    @staticmethod
    def _write_json(data: dict):
        with open("installed.json", "w+", encoding="UTF-8") as file:
            file.write(json.dumps(data, sort_keys=True, indent=4))


    @staticmethod
    def get_status(package_name: str, user: str) -> bool | None:
        """
        If True, package was successfully installed.

        If False, package had an error on installation.

        If None, package was never attempted to be installed.
        """

        data = InstalledCache._get_json()
        global_packages = data.get("OnlyRoot", {})
        local_packages = data.get("AnyUser", {}).get(user, {})

        if package_name in global_packages:
            return global_packages[package_name] == "installed"

        if package_name in local_packages:
            return local_packages[package_name] == "installed" 

        return None

    @staticmethod
    def set_global_status(package_name: str, status: bool | None):
        """
        Write to the cache if a OnlyRoot package was able to be installed or
        not.
        """
    
        template = {
            "OnlyRoot": {}
        }
        template.update(InstalledCache._get_json())
        template["OnlyRoot"][package_name] = status
        InstalledCache._write_json(template)

    @staticmethod
    def set_local_status(package_name: str, user: str, status: bool | None):
        """
        Write to the cache if a AnyUser package was able to be installed or
        not.
        """
    
        template = {
            "AnyUser": {
                user: {}
            }
        }
        template.update(InstalledCache._get_json())
        template["AnyUser"][user][package_name] = status
        InstalledCache._write_json(template)
        



