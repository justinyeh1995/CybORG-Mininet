import re

def update_config_file(file_path, new_ip, port=8000):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Use regex to replace localhost and port in api_connection_string
    updated_content = re.sub(
        r'(api_connection_string:\s*)(\S+)(:\d+)',
        'api_connection_string: ' + new_ip + f':{port}',
        content
    )
    
    with open(file_path, 'w') as file:
        file.write(updated_content)

if __name__ == "__main__":
    file_path = '/home/ubuntu/justinyeh1995/CASTLEGym/CybORG/CybORG/Mininet/actions/prog_test.yaml'  # Replace with the actual path to your YAML file
    new_ip = '10.0.37.234'  # Replace with the desired IP address
    new_port = 8000  # Replace with the desired port number
    update_config_file(file_path, new_ip, new_port)
    print(f"Updated config file. 'localhost' replaced with '{new_ip}' in api_connection_string.")
