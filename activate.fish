#!/usr/bin/env fish

function expand_bootstrap
    # Navigate to script directory
    cd (dirname (status --current-filename))

    # Install ansible
    if not command -q ansible
        if command -q apt-get
            sudo apt-get update
            sudo apt-get install -y ansible
        else
            echo (set_color red)"Error: No supported package manager found. Please install ansible manually."(set_color normal)
            exit 1
        end
    end

    # Install uv
    if not command -q uv
        curl -LsSf https://astral.sh/uv/install.sh | sh
        set -gx PATH $HOME/.local/bin/ $PATH
    end

    if not test -d .venv
        uv venv
    end

    source .venv/bin/activate.fish
    uv pip install -r requirements.txt
end

if test (id -u) -eq 0
    expand_bootstrap
    set -gx ACTIVATED_EXPAND ""
else
    echo (set_color red)"You must be root to run this script. Authenticate below to open a new shell and try again."(set_color normal)
    sudo su
end

