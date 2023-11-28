from HostProcessListingObservation import HostProcessListingObservation
from VelociraptorAction import VelociraptorAction
from CybORG.Simulator.State import State


class HostProcessListingAction(VelociraptorAction):

    def __init__(self, credentials_file):
        super().__init__(credentials_file)

        self.artifact_name = "Generic.System.Pstree"

    def execute(self, state: State):

        velociraptor_interface = self.get_velociraptor_interface()

        client_list = velociraptor_interface.get_client_list()

        hostname_process_list_dict = {}
        for client_dict in client_list:
            hostname = client_dict["os_info"]["hostname"]
            client_id = client_dict["client_id"]
            hostname_process_list_dict[hostname] = velociraptor_interface.execute_client_artifact(
                client_id, self.artifact_name
            )

        return HostProcessListingObservation(hostname_process_list_dict)
