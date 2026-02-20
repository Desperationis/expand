#!/usr/bin/env fish

function expand_bootstrap
    # Navigate to script directory
    cd (dirname (status --current-filename))

    # Install ansible
    if not command -q ansible
        if command -q apt-get
            sudo apt-get update
            sudo apt-get install -y ansible
        else if command -q brew
            sudo -u $SUDO_USER brew install ansible
        else if command -q dnf
            sudo dnf install -y ansible
        else if command -q yum
            sudo yum install -y ansible
        else if command -q pacman
            sudo pacman -S --noconfirm ansible
        else if command -q pipx
            pipx install --include-deps ansible
        else if command -q pip3
            pip3 install ansible 2>/dev/null; or pip3 install --break-system-packages ansible
        else if command -q pip
            pip install ansible 2>/dev/null; or pip install --break-system-packages ansible
        else
            echo (set_color red)"Error: No supported package manager found. Please install ansible manually."(set_color normal)
            exit 1
        end
    end

    # Install community.general Ansible collection (for homebrew modules)
    if not ansible-galaxy collection list 2>/dev/null | grep -q "community.general"
        ansible-galaxy collection install community.general
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
    sudo (command -s fish)
end

