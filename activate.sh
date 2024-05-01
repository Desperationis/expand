#!/usr/bin/env bash

expand_bootstrap() {
	# Navigate to same directory as this script
	cd "$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

	bash bootstrap/install_python.bash
	bash bootstrap/install_ansible.bash
	bash bootstrap/install_pip.bash
	bash bootstrap/install_venv.bash

	if ! [[ -d venv ]]
	then
		python3 -m venv venv
		. venv/bin/activate
		pip3 install -r requirements.txt
	else
		. venv/bin/activate
	fi
}

if ! [ "$(id -u)" = "0" ]; then
	echo -e "\033[1;31mThis script must be directly run as root, not as sudo.\033[0m"
else
	expand_bootstrap
	ACTIVATED_EXPAND=""
	export ACTIVATED_EXPAND 
fi

