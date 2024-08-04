import argparse

def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    parser.add_argument ("-mh", "--mininet_hostname", type=str, default="lan3h1", help="Mininet Hostname")
    # parse the args
    args = parser.parse_args ()

    return args

if __name__ == "__main__":
    parsed_args = parseCmdLineArgs ()
    
    mininet_hostname = parsed_args.mininet_hostname
    mininet_tmp_dir = f'/tmp/{mininet_hostname}/ubuntu'
    print(f'{mininet_tmp_dir}') 
    # observation=reset_action.execute(hostname, directory=f'/tmp/{mininet_hostname}/ubuntu')
    # print("observation is :",observation)
    # print('Success is:',observation.success)
    # print('md5 chksum are:',observation.md5)