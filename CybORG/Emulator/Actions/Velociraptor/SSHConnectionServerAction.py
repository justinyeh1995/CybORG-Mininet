import random
import string
from typing import Union

from CybORG.Emulator.Actions.Velociraptor.RunProcessAction import RunProcessAction
from CybORG.Emulator.Observations.Velociraptor.SSHConnectionServerObservation import SSHConnectionServerObservation
from CybORG.Shared import Observation
from CybORG.Simulator.State import State


class SSHConnectionServerAction(RunProcessAction):

    connection_key_size = 10

    @classmethod
    def get_connection_key(cls):
        return ''.join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.digits
            ) for _ in range(cls.connection_key_size)
        )

    def __init__(self, credentials_file, hostname, remote_hostname, remote_username, remote_password, client_port):

        self.connection_key = self.get_connection_key()

        super().__init__(
            credentials_file=credentials_file,
            hostname=hostname,
            command=f"python3 SSHConnectionServer.py -n {self.connection_key} -m {remote_hostname} -u {remote_username} -p {remote_password} -c {client_port} > /dev/null 2>&1 &"
        )

    def execute(self, state: Union[State, None]) -> Observation:

        process_observation = super().execute(state)

        return SSHConnectionServerObservation(process_observation, self.connection_key)
