#!/usr/bin/env bash

if ! [ "$(id -u)" = "0" ]; then
	echo -e "\033[1;31mThis script must be directly run as root, not as sudo.\033[0m"
	exit 1
fi


# All operations are done on top of `expand`
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

bash bootstrap/install_python.bash
bash bootstrap/install_ansible.bash
bash bootstrap/install_pip.bash
bash bootstrap/install_venv.bash

python3 -m venv venv
. venv/bin/activate

pip3 install -r requirements.txt
