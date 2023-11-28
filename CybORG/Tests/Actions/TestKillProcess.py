from CybORG.Simulator.Actions.EmulatedActions.VelociraptorActions.ProcessListingAction import ProcessListingAction
from CybORG.Simulator.Actions.EmulatedActions.VelociraptorActions.KillProcessAction import KillProcessAction
from CybORG.Simulator.Actions.EmulatedActions.VelociraptorActions.RunProcessAction import RunProcessAction


credentials_file = "prog_client.yaml"

create_foobar_action = RunProcessAction(
    credentials_file=credentials_file,
    hostname="TESTDOCKER1", command="""
cat > FOOBAR.sh <<END
while true; do
    sleep 10
done
END
"""
)

create_foobar_observation = create_foobar_action.execute(None)

run_foobar_action = RunProcessAction(
    credentials_file=credentials_file, hostname="TESTDOCKER1", command="bash FOOBAR.sh > /dev/null 2>&1 &"
)

run_foobar_observation = run_foobar_action.execute(None)

process_listing_action = ProcessListingAction(
    credentials_file=credentials_file,
    hostname="TESTDOCKER1"
)

process_listing_observation = process_listing_action.execute(None)

process_list = process_listing_observation.get_process_list()
for process in process_list:
    if "FOOBAR" in process.CommandLine:
        kill_process_action = KillProcessAction(
            credentials_file="prog_client.yaml",
            hostname="TESTDOCKER1",
            pid=process.Pid
        )

        kill_process_observation = kill_process_action.execute(None)
        print()