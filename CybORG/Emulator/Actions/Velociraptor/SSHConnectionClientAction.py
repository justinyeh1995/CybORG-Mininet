from .RunProcessAction import RunProcessAction


class SSHConnectionClientAction(RunProcessAction):

    def __init__(self, credentials_file, hostname, connection_key, command):

        super().__init__(
            credentials_file=credentials_file,
            hostname=hostname,
            command=f"echo '{command}' | /home/ubuntu/justinyeh1995/CASTLEGym/castle.3.venv/bin/python3 /home/ubuntu/justinyeh1995/castle-vm/Scripts/SSHConnectionClient.py {connection_key}"
        )
