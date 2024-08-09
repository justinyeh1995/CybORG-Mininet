#!bin/bash

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --python-path)
            PYTHON_PATH="$2"
            shift 2
            ;;
        --sys-script)
            SYS_SCRIPT="$2"
            shift 2
            ;;
        -n)
            # Keep other arguments to pass to the Python script
            conn_key+=("$2")
            shift 2
            ;;
    esac
done

# while getopts n: flag
# do
#     case "${flag}" in
#         n) conn_key=${OPTARG};;
#     esac
# done

echo "Connection Key is: $conn_key"


file_rm_cmd_output=$(echo 'rm cmd.sh && echo "Success" || echo "Failure"' | "$PYTHON_PATH" "$SYS_SCRIPT/SSHConnectionTerminalClient.py" "$conn_key")  
close_cmd_output=$(echo 'CLOSE' | "$PYTHON_PATH" "$SYS_SCRIPT/SSHConnectionTerminalClient.py" "$conn_key")  

echo "File removed is: $file_rm_cmd_output"
echo "Connection closed is: $close_cmd_output"

if [[ "$file_rm_cmd_output" == *"Success"* ]] && [[ "$close_cmd_output" == *"CLOSED"* ]]; then
    echo "Remove successful"
    echo "Sucess: TRUE"
    exit 0
else
    echo "Remove failed"
    echo "Sucess: FALSE"
    exit 1
fi



