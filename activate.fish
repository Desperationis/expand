#!/usr/bin/env fish

function expand_bootstrap
    # Navigate to the same directory as this script
    cd (cd (dirname (status --current-filename)) > /dev/null; pwd)

    bash bootstrap/install_python.bash
    bash bootstrap/install_ansible.bash
    bash bootstrap/install_pip.bash
    bash bootstrap/install_venv.bash

    if not test -d venv
        python3 -m venv venv
        . venv/bin/activate.fish
        pip3 install -r requirements.txt
    else
        . venv/bin/activate.fish
    end
end

if test (id -u) -eq 0
    expand_bootstrap
    set -x ACTIVATED_EXPAND ""
else
    echo -e "\e[31mYou must be root to run this script. Please switch to the root user and try again.\e[0m"
end

