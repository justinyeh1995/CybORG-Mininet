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
output="$($PYTHON_PATH $ACTION_FOLDER/ResetAction/reset_setup.py "${EXTRA_ARGS[@]}")"
IFS=',' read -r mininet_tmp_dir <<< "$output"

echo "Mininet Hostname tmp dir: $mininet_tmp_dir"

md5sum_cmd_output=$(md5sum $(find "$(realpath "$mininet_tmp_dir")" -maxdepth 1 -type f ! -name '.*' -exec echo "{}" +))

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
    echo "Sucess: TRUE"
    exit 0
else
    echo "Sucess: FALSE"
    echo "MD5SUM: "
    exit 1
fi