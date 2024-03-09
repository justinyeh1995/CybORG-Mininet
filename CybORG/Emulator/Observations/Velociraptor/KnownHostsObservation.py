from .ProcessObservation import ProcessObservation


class KnownHostsObservation(ProcessObservation):

    def __init__(self, process_observation):

        super().__init__(process_info=process_observation.artifact_info, success=process_observation.success)

        self.ip_address_list = self.Stdout.split()