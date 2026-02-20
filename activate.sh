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
        elif which brew > /dev/null 2>&1
        then
            sudo -u "$SUDO_USER" brew install ansible
        elif which dnf > /dev/null 2>&1
        then
            sudo dnf install -y ansible
        elif which yum > /dev/null 2>&1
        then
            sudo yum install -y ansible
        elif which pacman > /dev/null 2>&1
        then
            sudo pacman -S --noconfirm ansible
        elif which pipx > /dev/null 2>&1
        then
            pipx install --include-deps ansible
        elif which pip3 > /dev/null 2>&1
        then
            pip3 install ansible 2>/dev/null || pip3 install --break-system-packages ansible
        elif which pip > /dev/null 2>&1
        then
            pip install ansible 2>/dev/null || pip install --break-system-packages ansible
        else
            echo -e "\033[31mError: No supported package manager found. Please install ansible manually.\033[0m"
            exit 1
        fi
    fi

    # Install uv
	if ! which uv > /dev/null 2>&1
	then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH=$HOME/.local/bin/:$PATH
	fi


	if ! [[ -d .venv ]]
	then
        uv venv
	fi

    . .venv/bin/activate
    uv pip install -r requirements.txt
}


if [ "$(id -u)" -eq 0 ]
then
	expand_bootstrap
	ACTIVATED_EXPAND=""
	export ACTIVATED_EXPAND 
else
    echo -e "\e[31mYou must be root to run this script. Authenticate below to open a new shell and try again.\e[0m"
    sudo "$(command -v bash)"
fi
