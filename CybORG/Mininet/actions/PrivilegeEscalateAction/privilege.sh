#!/bin/bash

# Read input from Python script
echo "Starting script..."
output="$(/home/ubuntu/justinyeh1995/CASTLEGym/castle.2.venv/bin/python3 /home/ubuntu/justinyeh1995/CASTLEGym/CybORG/CybORG/Mininet/actions/PrivilegeEscalateAction/privilege_setup.py "$@")"
echo "Python script output: $output"
IFS=',' read -r conn_key ip file_path <<< "$output"

echo "Remote IP: $ip"
echo "Connection Key is: $conn_key"
echo "File Path is: $file_path"

# Continue with the rest of the script
find_new_host_cmd_output=$(echo 'grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' '$file_path'' | /home/ubuntu/justinyeh1995/CASTLEGym/castle.2.venv/bin/python3 /home/ubuntu/justinyeh1995/CASTLEGym/CybORG/CybORG/Mininet/systems/scripts/SSHConnectionTerminalClient.py "$conn_key")  

ip_string_cmd_output=$(echo 'ss -tunap | grep ':$port'' | /home/ubuntu/justinyeh1995/CASTLEGym/castle.2.venv/bin/python3 /home/ubuntu/justinyeh1995/CASTLEGym/CybORG/CybORG/Mininet/systems/scripts/SSHConnectionTerminalClient.py "$conn_key")

if [ "$find_new_host_cmd_output" != "" ]; then
    echo "Any new host explored?: $find_new_host_cmd_output"
    echo "Sucess: TRUE"
    exit 0
else
    echo "Sucess: FALSE"
    echo "Any new host explored?: "
    exit 1 
fi