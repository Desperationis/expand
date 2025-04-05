#!/usr/bin/env bash

expand_bootstrap() {
	# Navigate to same directory as this script
	cd "$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

    # Install ansible
    if ! which ansible > /dev/null 2>&1
    then
        if which apt-get > /dev/null 2>&1
        then
            sudo apt-get update
            sudo apt-get install -y ansible
        else
            echo -e "\033[31mError: No supported package manager found. Please install ansible manually.\033[0m"
            exit 1
        fi
    fi

    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add uv to path
    export PATH=$HOME/.local/bin/:$PATH

	if ! [[ -d .venv ]]
	then
        uv venv
	fi

    . venv/bin/activate
    uv pip install -r requirements.txt
}


if [ "$(id -u)" -eq 0 ]
then
	expand_bootstrap
	ACTIVATED_EXPAND=""
	export ACTIVATED_EXPAND 
else
	 echo -e "\e[31mYou must be root to run this script. Please switch to the root user and try again.\e[0m"
fi
