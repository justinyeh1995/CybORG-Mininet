import json
import argparse
import inspect
import base64

def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    parser.add_argument ("-mininet_hostname", "--mininet_hostname", type=str, default="lan3h1", help="Mininet Hostname")
    parser.add_argument ("-data", "--additional_data", help="Additional data as base64 encoded JSON string")
    # parse the args
    args = parser.parse_args ()

    return args

if __name__ == "__main__":
    parsed_args = parseCmdLineArgs ()
    mininet_hostname = parsed_args.mininet_hostname

    previous_verification_dict = {}
    if parsed_args.additional_data:
        json_str = base64.b64decode(parsed_args.additional_data).decode('utf-8')
        previous_verification_dict = json.loads(json_str)
    
    mininet_tmp_dir = f'/tmp/{mininet_hostname}/ubuntu'
    print(f'{mininet_tmp_dir},{previous_verification_dict}')

    # string = json.dumps(verify_files_observation.get_verification_dict(), indent=4, sort_keys=True)
    # low_density_files= verify_files_observation.get_different_checksum_file_list()
    # #print('Verify file observation:',verify_files_observation.__dict__)
    # print('\n-> Checksums are:',string,'type is:',type(string))
    # print('low density files are:', low_density_files)
    # print("End")