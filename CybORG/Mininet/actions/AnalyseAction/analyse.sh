#!/bin/bash

# Read input from Python script
echo "Starting script..."
output="$(/home/ubuntu/justinyeh1995/CASTLEGym/castle.2.venv/bin/python3  /home/ubuntu/justinyeh1995/CASTLEGym/CybORG/CybORG/Mininet/actions/ResetAction/reset_setup.py "$@")"
IFS=',' read -r mininet_tmp_dir <<< "$output"

echo "Mininet Hostname tmp dir: $mininet_tmp_dir"

md5sum_cmd_output=$(md5sum $(find "$(realpath "$mininet_tmp_dir")" -maxdepth 1 -type f ! -name '.*' -exec echo "{}" +))
densityscount_cmd_output=$(densityscout -d "$(realpath "$mininet_tmp_dir")")

# Declare an associative array (requires Bash 4.0 or later)
declare -A current_verification_dict

# Read the md5 output line by line
while IFS= read -r line; do
    # Skip empty lines
    [ -z "$line" ] && continue
    
    # Split the line into value and key
    read -r value key <<< "$line"
    
    # Store in the associative array
    current_verification_dict["$key"]="$value"
done <<< "$md5sum_cmd_output"

if [ "$md5sum_cmd_output" != "" ]; then
    # Format the dictionary as a string
    dict_string="{"
    first=true
    for key in "${!current_verification_dict[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            dict_string+=","
        fi
        dict_string+="'$key': '${current_verification_dict[$key]}'"
    done
    dict_string+="}"
    echo "MD5SUM: $dict_string"
    # echo "Sucess: TRUE"
    # exit 0
else
    echo "Sucess: FALSE"
    echo "MD5SUM: "
    exit 1
fi

