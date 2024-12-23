fish_config theme choose fish\ default

function dcopy
    xclip -selection clipboard
end

function dpaste
    xclip -selection clipboard -o
end

function iso_write
    if test (count $argv) -ne 2
        echo "Usage: iso_write <path_to_iso> <device>"
        return 1
    end

    set iso_path $argv[1]
    set device $argv[2]

    sudo dd bs=4M if=$iso_path of=$device status=progress oflag=sync
end


function mount_thing
    if test (count $argv) -ne 1
        echo "Usage: mount_thing <device>"
        return 1
    end

    set device $argv[1]
    set random_folder (string join '' 'usb' (random 1000 9999))
    set dir_path /media/$USER/$random_folder

    sudo mkdir -p $dir_path
    if sudo mount $device $dir_path
        echo "Mounted $device to $dir_path"
    else
        echo "Failed to mount $device"
        sudo rmdir $dir_path
        return 1
    end
end

function umount_thing
    if test (count $argv) -ne 1
        echo "Usage: umount_thing <mount_path>"
        return 1
    end

    set mount_path $argv[1]

    if not test -d $mount_path
        echo "Error: $mount_path is not a valid directory"
        return 1
    end

    if sudo umount $mount_path
        sudo rmdir $mount_path
        echo "Unmounted and removed $mount_path"
    else
        echo "Failed to unmount $mount_path"
        return 1
    end
end





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

	echo ""
	echo  "           (              "			(welcome_message)
	echo  "            )             "
	echo  "           (              "			(show_os_info)	
	echo  "     /\\  .-\"\"\"-.  /\\      "		(show_cpu_cores)
	echo  "    //\\\\/  ,,,  \\//\\\\     "		(show_cpu_processors)
	echo  "    |/\\| ,;;;;;, |/\\|     "		
	echo  "    //\\\\\\;-\"\"\"-;///\\\\     "	(show_wifi_ssid)
	echo  "   //  \\/   .   \\/  \\\\    "		(show_ip)
	echo  "  (| ,-_| \\ | / |_-, |)   "			(show_gateway)
	echo  "    //`__\\.-.-./__`\\\\     "		(show_nc_count)
	echo  "   // /.-(() ())-.\\ \\\\    "
	echo  "  (\\ |)   '---'   (| /)   "			(show_hostname)
	echo  "   ` (|           |) `    "			(show_bluetooth)
	echo  "     \\)           (/      "			(show_timezone)
	echo ""
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
        set formatted_uptime $up_time"utes"
    case '*'
        set formatted_uptime "$formatted_uptime hours"
    end

    echo -en " Today is "
    set_color brblue
    echo -en (date +%m/%d/%Y)
    set_color normal
    echo -en ", up for "
    set_color brblue
    echo -en "$formatted_uptime"
    set_color normal
    echo -en "."
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
	fish_add_path ~/box/bin
	fish_add_path ~/.local/bin

	if which zoxide > /dev/null 2>&1
		zoxide init fish | source
	end

    #alias rm 'rmtrash'
    #alias rmdir 'rmdirtrash'
    #alias sudo 'sudo '

	if test -f ~/anaconda3/bin/conda
		fish_add_path ~/anaconda3/bin/
		eval ~/anaconda3/bin/conda "shell.fish" "hook" $argv | source
		if ! conda env list | grep -q "\bcustom\b"
			echo "`custom` environment not created, creating..."
			conda create -n custom --yes
		end

		conda activate custom
	end

	#[ -z "$TMUX" ] && exec tmux
end

