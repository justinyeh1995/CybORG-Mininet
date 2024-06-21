# import json

from CybORG.Emulator.Actions.Velociraptor.ImpactAction import ImpactAction

credentials_file = "prog_client3.yaml"

haraka_exploit_action = ImpactAction(
    credentials_file=credentials_file,
    hostname="TESTDOCKER1",
    connection_key="NYON35VSNR",
    reverse_shell_server_port=4444,
    reverse_shell_command="ip addr"
)

haraka_exploit_observation = haraka_exploit_action.execute(None)

print("foo")