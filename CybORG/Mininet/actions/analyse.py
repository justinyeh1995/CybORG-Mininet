import json
import argparse
import inspect
import base64

from CybORG import CybORG
from CybORG.Emulator.Actions.Velociraptor.Analyse import AnalyseAction
from CybORG.Emulator.Observations.Velociraptor import AnalyseObservation

def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    parser.add_argument ("-host", "--hostname", default="cpswtjustin", help="Hostname, use hostname to figure out hostname")
    parser.add_argument ("-mininet_hostname", "--mininet_hostname", type=str, default="lan3h1", help="Mininet Hostname")
    parser.add_argument ("-remote", "--remote_hostname", default="0.0.0.0", help="Remote IP Address")
    parser.add_argument ("-data", "--additional_data", help="Additional data as base64 encoded JSON string")
    # parse the args
    args = parser.parse_args ()

    return args

if __name__ == "__main__":
    parsed_args = parseCmdLineArgs ()
    
    path = str(inspect.getfile(CybORG))
    path = path[:-10]
    credentials_file = f"{path}/Mininet/actions/prog_client.yaml"  # @To-Do make it configurable
        
    # previous_verification_dict = {
    #     "/home/ubuntu/Tomcat": "2e0c9cca79009b53b5a0288f5cba9ace",
    #     "/home/ubuntu/adhoc.sh": "bccf1957d9b0767eb0021fe72a418855",
    #     "/home/ubuntu/cmd.sh": "c67e0b30a5440c8c52bc607d9e239a17",
    #     "/home/ubuntu/decoy_connections.log": "cafb0485971517dcec21dde8622235dc",
    #     "/home/ubuntu/densityscout": "0fa707b2ff211cf488adfe4cc937bfbf",
    #     "/home/ubuntu/make_ssh_connection.sh": "c1dd4e9a93ffae5bbcd775b73664b686",
    #     "/home/ubuntu/start_velociraptor_client.sh": "e203ac462ebb0c3680fddacd3d109c21",
    #     "/home/vagrant/velociraptor_client_0.7.1_amd64.deb": "02c50b30aeda38a0ca219a7d5f2dc011"
    # } 

    hostname = parsed_args.hostname
    mininet_hostname = parsed_args.mininet_hostname

    previous_verification_dict = {}
    if parsed_args.additional_data:
        json_str = base64.b64decode(parsed_args.additional_data).decode('utf-8')
        previous_verification_dict = json.loads(json_str)
    
    verify_files_action = AnalyseAction(
        credentials_file=credentials_file,
        hostname=hostname,
        directory=f'/tmp/{mininet_hostname}/ubuntu',
        previous_verification_dict=previous_verification_dict
    )

    verify_files_observation: AnalyseObservation = verify_files_action.execute(None)

    string = json.dumps(verify_files_observation.get_verification_dict(), indent=4, sort_keys=True)
    low_density_files= verify_files_observation.get_different_checksum_file_list()
    #print('Verify file observation:',verify_files_observation.__dict__)
    print('\n-> Checksums are:',string,'type is:',type(string))
    print('low density files are:', low_density_files)
    print("End")