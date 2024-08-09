#!bin/bash

while getopts n: flag
do
    case "${flag}" in
        n) conn_key=${OPTARG};;
    esac
done

echo "Connection Key is: $conn_key"


file_rm_cmd_output=$(echo 'rm cmd.sh && echo "Success" || echo "Failure"' | /home/ubuntu/justinyeh1995/CASTLEGym/castle.2.venv/bin/python3 /home/ubuntu/justinyeh1995/CASTLEGym/CybORG/CybORG/Mininet/systems/scripts/SSHConnectionTerminalClient.py "$conn_key")  
close_cmd_output=$(echo 'CLOSE' | /home/ubuntu/justinyeh1995/CASTLEGym/castle.2.venv/bin/python3 /home/ubuntu/justinyeh1995/CASTLEGym/CybORG/CybORG/Mininet/systems/scripts/SSHConnectionTerminalClient.py "$conn_key")  

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



