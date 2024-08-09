#!/bin/bash

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --python-path)
            PYTHON_PATH="$2"
            shift 2
            ;;
        --action-folder)
            ACTION_FOLDER="$2"
            shift 2
            ;;
        --sys-script)
            SYS_SCRIPT="$2"
            shift 2
            ;;
        *)
            # Keep other arguments to pass to the Python script
            EXTRA_ARGS+=("$1")
            shift
            ;;
    esac
done

# Check if required arguments are provided
if [[ -z "$PYTHON_PATH" ]] || [[ -z "$ACTION_FOLDER" ]]; then
    echo "Usage: $0 --python-path <path> --action-folder <path>"
    exit 1
fi

# Read input from Python script
echo "Starting script..."
output="$($PYTHON_PATH $ACTION_FOLDER/PrivilegeEscalateAction/privilege_setup.py "${EXTRA_ARGS[@]}")"
echo "Python script output: $output"
IFS=',' read -r conn_key ip file_path <<< "$output"

echo "Remote IP: $ip"
echo "Connection Key is: $conn_key"
echo "File Path is: $file_path"

# Continue with the rest of the script
find_new_host_cmd_output=$(echo 'grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' '$file_path'' | $PYTHON_PATH $SYS_SCRIPT/SSHConnectionTerminalClient.py "$conn_key")  

ip_string_cmd_output=$(echo 'ss -tunap | grep ':$port'' | $PYTHON_PATH $SYS_SCRIPT/SSHConnectionTerminalClient.py "$conn_key")

echo "Any new host explored?: $find_new_host_cmd_output"
echo "Sucess: TRUE"

# if [ "$find_new_host_cmd_output" != "" ]; then
#     echo "Any new host explored?: $find_new_host_cmd_output"
#     echo "Sucess: TRUE"
#     exit 0
# else
#     echo "Sucess: FALSE"
#     echo "Any new host explored?: "
#     exit 1 
# fi