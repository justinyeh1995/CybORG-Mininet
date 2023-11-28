from CybORG.Shared import Observation
from CybORG.Simulator.State import State

from .ProcessObservation import ProcessObservation
from .VelociraptorAction import VelociraptorAction


class RunProcessAction(VelociraptorAction):

    def __init__(self, credentials_file, hostname, command):

        super().__init__(credentials_file=credentials_file)

        self.hostname = hostname
        self.artifact_name = "Linux.Sys.BashShell"
        self.environment_dict = {"Command": f"{command}"}

    def execute(self, state: State) -> Observation:

        velociraptor_interface = self.get_velociraptor_interface()

        client_id = velociraptor_interface.get_client_id_from_hostname(self.hostname)

        output_list = velociraptor_interface.execute_client_artifact(
            client_id, self.artifact_name, self.environment_dict
        )

        return ProcessObservation(
            success=False
        ) if output_list is None else ProcessObservation(
            process_info=output_list[0], success=True
        )