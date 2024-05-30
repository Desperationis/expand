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

expand_bootstrap
set -gx ACTIVATED_EXPAND ""
