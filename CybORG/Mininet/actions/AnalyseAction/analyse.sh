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
output=$("$PYTHON_PATH" "$ACTION_FOLDER/AnalyseAction/analyse_setup.py" "${EXTRA_ARGS[@]}")
IFS=',' read -r mininet_tmp_dir previous_verification_dict_string <<< "$output"

echo "Mininet Hostname tmp dir: $mininet_tmp_dir"
# echo "Previous MD5SUM String: $previous_verification_dict_string"

# 2. Run md5sum on all files in the directory
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
    current_verification_dict_string="{"
    first=true
    for key in "${!current_verification_dict[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            current_verification_dict_string+=","
        fi
        current_verification_dict_string+="'$key': '${current_verification_dict[$key]}'"
    done
    current_verification_dict_string+="}"
fi

#3. Run densityscout
densityscount_cmd_output=$(densityscout -d "$(realpath "$mininet_tmp_dir")")

declare -A densityscount_dict

# Read the densityscout output line by line
while IFS='|' read -r value key; do
    # Skip empty lines
    [ -z "$value" ] && [ -z "$key" ] && continue
    
    # Trim leading/trailing whitespace
    value=$(echo "$value" | xargs)
    key=$(echo "$key" | xargs)
    
    # Store in the associative array
    densityscount_dict["$key"]="$value"
done <<< "$densityscount_cmd_output"

if [ "$densityscount_cmd_output" != "" ]; then
    densityscount_dict_string="{"
    first=true
    for key in "${!densityscount_dict[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            densityscount_dict_string+=","
        fi
        densityscount_dict_string+="'$key': '${densityscount_dict[$key]}'"
    done
    densityscount_dict_string+="}"
fi

if test "$current_verification_dict_string" != "" && test "$previous_verification_dict_string" != "" && test "$densityscount_cmd_output" != ""; then
    echo "Sucess: TRUE"
    echo "Previous MD5SUM: $previous_verification_dict_string"
    echo "Current MD5SUM: $current_verification_dict_string"
    echo "Densityscout: $densityscount_dict_string"
else
    echo "Sucess: FALSE"
    echo "Previous MD5SUM: $previous_verification_dict_string"
    echo "Current MD5SUM: $current_verification_dict_string"
    echo "Densityscout: $densityscount_dict_string"
    exit 1
fi
