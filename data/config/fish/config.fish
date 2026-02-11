fish_config theme choose fish\ default

function fish_prompt

	if fish_is_root_user
		set_color brred
	else
		set_color brblue
	end
	printf '%s' (whoami)
	set_color normal
	printf ' at '

	set_color brmagenta
	printf '%s' (hostname|cut -d . -f 1)
	set_color normal
	printf ' in '

	set_color brgreen
	printf '%s ' (prompt_pwd --full-length-dirs=2)
	set_color normal
	printf '%s' (__fish_git_prompt)

	# Line 2
	echo
	if test $VIRTUAL_ENV
	  printf "(%s) " (set_color blue)(basename $VIRTUAL_ENV)(set_color normal)
	end
	printf '↪  '
	set_color normal
end



function fish_right_prompt

	# Last command status
	set -l code $status
	if test $code != 0
		echo -s (set_color brred) '-' $code '- '
	end

	# Timestamp
	set_color brblack
	echo (date "+%H:%M:%S")
	set_color normal


end






function fish_greeting -d "Greeting message on shell session start up"
    set ascii_art (cat ~/.config/fish/ascii_art.txt | string split0)

    # This assumes 'welcome_message', 'show_os_info', etc., are functions
    # or commands that output the desired values.
    set -l values \
        (welcome_message) \
        (show_os_info) \
        (show_cpu_cores) \
        (show_cpu_processors) \
        (show_wifi_ssid) \
        (show_ip) \
        (show_gateway) \
        (show_nc_count) \
        (show_hostname) \
        (show_bluetooth) \
        (show_timezone)

    # Corrected loop: uses (count) instead of (math (count)) and $values[$i] for indexing.
    for i in (seq 1 (count $values))
        set ascii_art (string replace -r "\{$i\}" -- $values[$i] $ascii_art | string split0 | head -n -2 | string split0)
    end

    echo
    echo $ascii_art
end


function welcome_message -d "Say welcome to user"
    set_color brblue
    echo -en "@"
    echo -en (whoami)
    set_color normal

    set --local up_time (uptime | cut -d "," -f1 | cut -d "p" -f2 | sed 's/^ *//g')

    set --local time (echo $up_time | cut -d " " -f2)
    set --local formatted_uptime $time

    switch $time
    case "days" "day"
        set formatted_uptime "$up_time"
    case "min"
        set formatted_uptime $up_time
    case '*'
        set formatted_uptime "$formatted_uptime hours"
    end

    echo -en " "
    set_color brblue
    echo -en (date +%m/%d/%Y)
    set_color normal
    echo -en ", up for "
    set_color brblue
    echo -en "$formatted_uptime"
    set_color normal
end

function show_os_info -d "Prints operating system info"
	set --local os_type (uname -s)
	set --local os_name "$os_type"

	if test "$os_type" = "Linux"
		if test -f /etc/os-release
			# freedesktop.org and systemd
			set --local OS ( bash -c ". /etc/os-release && echo -en \$NAME" )
			set --local VER ( bash -c ". /etc/os-release && echo -en \$VERSION_ID" )
			set os_name $OS $VER
		else if type lsb_release >/dev/null 2>&1
			# linuxbase.org
			set --local OS (lsb_release -si)
			set --local VER (lsb_release -sr)
			set os_name $OS $VER
		else if test -f /etc/lsb-release
			# For some versions of Debian/Ubuntu without lsb_release command
			set --local OS (bash -c ". /etc/lsb-release && echo -en \$DISTRIB_ID")
			set --local VER (bash -c ". /etc/lsb-release && echo -en \$DISTRIB_RELEASE")
			set os_name $OS $VER
		else if test -f /etc/debian_version
			# Older Debian/Ubuntu/etc.
			set --local OS "Debian"
			set --local VER (cat /etc/debian_version)
			set os_name $OS $VER
		else if test -f /etc/SuSe-release
			# Older SuSE/etc.
			set os_name "SuSe"
		else if test -f /etc/redhat-release
			# Older Red Hat, CentOS, etc.
			set os_name "RedHat"
		end
	end

    set_color brmagenta
    echo -en "OS: "
    set_color normal
    echo -en $os_name
end

function show_cpu_cores -d "Prints # of cores"
	set --local os_type (uname -s)
	set --local cores ""

	if test "$os_type" = "Linux"
		set cores (grep "cpu cores" /proc/cpuinfo | head -1 | cut -d ":"  -f2 | tr -d " ")
	else if test "$os_type" = "Darwin"
		set cores (system_profiler SPHardwareDataType | grep "Cores" | cut -d ":" -f2 | tr -d " ")
	end

	set_color brmagenta
	echo -en "CPU Cores: "
	set_color normal
	echo -en "$cores"
end

function show_cpu_processors -d "Prints # of processors"
	set --local os_type (uname -s)
	set --local procs ""

	if test "$os_type" = "Linux"
        set procs (nproc)
	else if test "$os_type" = "Darwin"
        set procs (system_profiler SPHardwareDataType | grep "Number of Processors" | cut -d ":" -f2 | tr -d " ")
	end

	set_color brmagenta
	echo -en "CPU Processors: "
	set_color normal
	echo -en "$procs"
end

function show_cpu_name -d "Prints out CPU name"
	set --local os_type (uname -s)
	set --local cpu_name ""

	if test "$os_type" = "Linux"
        set cpu_name (grep "model name" /proc/cpuinfo | head -1 | cut -d ":" -f2)
	else if test "$os_type" = "Darwin"
        set cpu_name (system_profiler SPHardwareDataType | grep "Processor Name" | cut -d ":" -f2 | tr -d " ")
	end

	set_color brmagenta
	echo -en "CPU: "
	set_color normal
	echo -en "$cpu_name"
end

function show_hostname -d "Prints out hostname"
    set --local os_type (uname -s)
    set --local hname "N/A"

	if test "$os_type" = "Linux"
        set hname (hostname|cut -d . -f 1)
    end

    set_color brblack
    echo -en "Hostname: "
    set_color normal
    echo -en "$hname"
end

function show_nc_count -d "Prints out # of network devices"
    set --local os_type (uname -s)
    set --local nc_count "N/A"

	if test "$os_type" = "Linux"
        set nc_count (ip -o link show | wc -l)
    end

    set_color brblack
    echo -en "Network Devices: "
    set_color normal
    echo -en "$nc_count"
end

function show_ip -d "Print out IP of network card"
    set --local os_type (uname -s)
    set --local ip "N/A"

	if test "$os_type" = "Linux"
		if which iwgetid > /dev/null 2>&1
			if iwgetid -r > /dev/null 2>&1
				set ip (ip address show | grep -E "inet .* brd .* dynamic" | cut -d " " -f6)
			end
		end
	else if test "$os_type" = "Darwin"
        set ip (ifconfig | grep -v "127.0.0.1" | grep "inet " | head -1 | cut -d " " -f2)
    end

    set_color brblack
    echo -en "IP: "
    set_color normal
    echo -en "$ip"
end

function show_gateway -d "Print out default gateway of network card"
    set --local os_type (uname -s)
    set --local gw "N/A"

	if test "$os_type" = "Linux"
		if which iwgetid > /dev/null 2>&1
			if iwgetid -r > /dev/null 2>&1
				set gw (ip route | grep default | cut -d " " -f3)
			end
		end
	else if test "$os_type" = "Darwin"
        set gw (netstat -nr | grep -E "default.*UGSc" | cut -d " " -f13)
    end

    set_color brblack
    echo -en "Gateway: "
    set_color normal
    echo -en "$gw"
end

function show_wifi_ssid -d "Print out Wifi SSID"
    set --local os_type (uname -s)
    set --local w_status "N/A"

	if test "$os_type" = "Linux"
		if which iwgetid > /dev/null 2>&1
			if iwgetid -r > /dev/null 2>&1
				set w_status (iwgetid -r )
			else
				set w_status "Not connected"
			end
		end
    end

    set_color brblack
    echo -en "Wifi: "
    set_color normal
    echo -en "$w_status"
end

function show_bluetooth -d "Print out bluetooth status"
    set --local os_type (uname -s)
    set --local b_status "N/A"

	if test "$os_type" = "Linux"
		if which hcitool > /dev/null 2>&1
			if test $(hcitool dev | wc -l) -gt 1
				set b_status "ON"
			end
		else
			set b_status "OFF"
		end
    end

    set_color brblack
    echo -en "Bluetooth: "
    set_color normal
    echo -en "$b_status"
end

function show_timezone -d "Show local timezone"
    set --local os_type (uname -s)
    set --local timezone "N/A"

	if test "$os_type" = "Linux"
		set timezone (date +"%Z")
    end

    set_color brblack
    echo -en "Timezone: "
    set_color normal
    echo -en "$timezone"
end

if status is-interactive
    # Matches what I put in /etc/profile.d/
	fish_add_path ~/box/bin
	fish_add_path ~/.local/bin
	fish_add_path ~/.cargo/bin
    fish_add_path ~/.julia/juliaup/julia-1.11.3+0.x64.linux.gnu/bin


	if which zoxide > /dev/null 2>&1
		zoxide init fish | source
	end

	if test -f ~/anaconda3/bin/conda
		fish_add_path ~/anaconda3/bin/
		eval ~/anaconda3/bin/conda "shell.fish" "hook" $argv | source
		if ! conda env list | grep -q "\bcustom\b"
			echo "`custom` environment not created, creating..."
			conda create -n custom --yes
		end

		conda activate custom
	end

    if which tmux >/dev/null && [ -z "$TMUX" ]
        tmux attach-session -t default >/dev/null || tmux new-session -s default >/dev/null
    end

    export CUDA_HOME=/usr/local/cuda
    fish_add_path {$CUDA_HOME}/bin
    export LD_LIBRARY_PATH={$CUDA_HOME}/lib64:$LD_LIBRARY_PATH
    fish_add_path $(npm prefix -g)/bin
end


# pnpm
set -gx PNPM_HOME "/home/adhoc/.local/share/pnpm"
if not string match -q -- $PNPM_HOME $PATH
  set -gx PATH "$PNPM_HOME" $PATH
end
# pnpm end
