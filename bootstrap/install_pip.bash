#!/usr/bin/env bash
#
if ! which python3 > /dev/null 2>&1
then
    echo -e "\033[31mpython3 is not installed. You shouldn't see this.\033[0m"
	exit 1
fi

if ! which pip3 >/dev/null 2>&1; then
    echo -e "\033[31mpip3 is not installed.\033[0m"

    # Check which package manager is available and install pip3
    if command -v apt-get &>/dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3-pip
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3-pip
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3-pip
    elif command -v pacman &>/dev/null; then
        sudo pacman -Sy python-pip --noconfirm
    elif command -v zypper &>/dev/null; then
        sudo zypper install -y python3-pip
    else
        echo -e "\033[31mError: No supported package manager found. Please install pip3 manually.\033[0m"
        exit 1
    fi

    # Check if installation was successful
    if ! command -v pip3 &>/dev/null; then
        echo -e "\033[31mError: Failed to install pip3. Please install it manually.\033[0m"
        exit 1
    fi

    echo -e "\033[0;32mpip3 has been successfully installed.\033[0m"
else
    echo -e "\033[36mpip3 is installed.\033[0m"
fi

