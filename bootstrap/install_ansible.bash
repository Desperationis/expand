#!/usr/bin/env bash

if ! which ansible >/dev/null 2>&1; then
    echo -e "\033[31mansible is not installed.\033[0m"

    # Check which package manager is available and install ansible
    if command -v apt-get &>/dev/null; then
        sudo apt-get update
        sudo apt-get install -y ansible
    elif command -v yum &>/dev/null; then
        sudo yum install -y ansible
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y ansible
    elif command -v pacman &>/dev/null; then
        sudo pacman -Sy ansible --noconfirm
    elif command -v zypper &>/dev/null; then
        sudo zypper install -y ansible
    else
        echo -e "\033[31mError: No supported package manager found. Please install ansible manually.\033[0m"
        exit 1
    fi

    # Check if installation was successful
    if ! command -v ansible &>/dev/null; then
        echo -e "\033[31mError: Failed to install ansible. Please install it manually.\033[0m"
        exit 1
    fi

    echo -e "\033[0;32mansible has been successfully installed.\033[0m"
else
    echo -e "\033[36mansible is installed.\033[0m"
fi

