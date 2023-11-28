from .ProcessListingObservation import ProcessListingObservation
from .VelociraptorAction import VelociraptorAction
from CybORG.Simulator.State import State


class ProcessListingAction(VelociraptorAction):

    def __init__(self, credentials_file, hostname):
        super().__init__(credentials_file=credentials_file)

        self.hostname = hostname
        self.artifact_name = "Generic.System.Pstree"

    def execute(self, state: State) -> ProcessListingObservation:

        velociraptor_interface = self.get_velociraptor_interface()

        client_id = velociraptor_interface.get_client_id_from_hostname(self.hostname)

        process_list = velociraptor_interface.execute_client_artifact(client_id, self.artifact_name)

        return ProcessListingObservation(success=False) if process_list is None else ProcessListingObservation(
            process_list=process_list, success=True
        )
