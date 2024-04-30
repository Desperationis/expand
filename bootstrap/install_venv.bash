#!/usr/bin/env bash

if ! which python3 > /dev/null 2>&1
then
    echo -e "\033[31mpython3 is not installed. You shouldn't see this.\033[0m"
	exit 1
fi



if ! python3 -m venv --help >/dev/null 2>&1; then
    echo -e "\033[31mpython3-venv is not installed.\033[0m"

    # Check which package manager is available and install python3-venv
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y python3-venv
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3-venv
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3-venv
    elif command -v pacman &> /dev/null; then
        sudo pacman -Sy python3-venv --noconfirm
    elif command -v zypper &> /dev/null; then
        sudo zypper install -y python3-venv
    else
        echo -e "\033[31mError: No supported package manager found. Please install python3-venv manually.\033[0m"
        exit 1
    fi

    # Check if installation was successful
    if ! python3 -m venv --help >/dev/null 2>&1; then
        echo -e "\033[31mError: Failed to install python3-venv. Please install it manually.\033[0m"
        exit 1
    fi

    echo -e "\033[0;32mpython3-venv has been successfully installed.\033[0m"
else
    echo -e "\033[36mpython3-venv is installed.\033[0m"
fi
