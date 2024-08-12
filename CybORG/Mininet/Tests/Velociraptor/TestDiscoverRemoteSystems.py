import inspect
from CybORG import CybORG
from CybORG.Emulator.Actions.Velociraptor.DiscoverRemoteSystemsAction import DiscoverRemoteSystemsAction

path = str(inspect.getfile(CybORG))
path = path[:-10]
credentials_file = f"{path}/Mininet/actions/prog_client.yaml"  # @To-Do make it configurable

discover_remote_systems_action = DiscoverRemoteSystemsAction(
    credentials_file=credentials_file,
    hostname='cpswtjustin',
    cidr='10.0.112.0/28'
)

observation = discover_remote_systems_action.execute(None)
print('success is:',observation.success)
print('IP Address list is:',observation.ip_address_list)
print("foo")
