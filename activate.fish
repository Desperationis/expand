#!/usr/bin/env fish

function expand_bootstrap
    # Navigate to the same directory as this script
    cd (dirname (status --current-filename))

    bash bootstrap/install_python.bash
    bash bootstrap/install_ansible.bash
    bash bootstrap/install_pip.bash
    bash bootstrap/install_venv.bash

    if not test -d venv
        python3 -m venv venv
        source venv/bin/activate.fish
        pip3 install -r requirements.txt
    else
        source venv/bin/activate.fish
    end
end

if not test (id -u) -eq 0
    echo -e "\033[1;31mThis script must be directly run as root, not as sudo.\033[0m"
else
    expand_bootstrap
    set -gx ACTIVATED_EXPAND ""
end

