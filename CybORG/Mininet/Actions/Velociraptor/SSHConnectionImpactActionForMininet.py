from .RunProcessAction import RunProcessAction
import inspect
from CybORG import CybORG

class SSHConnectionImpactAction(RunProcessAction):

    def __init__(self, credentials_file, hostname, connection_key, command):
        path = str(inspect.getfile(CybORG))
        path = path[:-10]
        super().__init__(
            credentials_file=credentials_file,
            hostname=hostname,
            command=f"echo '{command}' | " + 
                    f"/home/ubuntu/justinyeh1995/CASTLEGym/castle.2.venv/bin/python3 {path}/Mininet/systems/scripts/SSHConnectionTerminalClient.py {connection_key}"
        )
        