#!/usr/bin/python3

import argparse
import json
from pathlib import Path
import psutil
import sys
import zmq


class SSHConnectionTerminalClient:

    def __init__(self, connection_key):

        self.connection_key = connection_key

        self.socket_path = Path(f"/tmp/terminal_connection_{connection_key}")

        self.ssh_connection_server_pid_file = Path(
            "/", "usr", "local", "run", f"SSHConnectionServer_{connection_key}.pid"
        )

    def check_ssh_connection_server_running(self):

        bad_pid = True

        if self.ssh_connection_server_pid_file.is_file():
            with self.ssh_connection_server_pid_file.open("r") as input_fd:
                pid_string = input_fd.readline().strip()

            if pid_string.isnumeric():
                pid = int(pid_string)

                if psutil.pid_exists(pid):
                    bad_pid = False

        if bad_pid:
            print(f"SSHConnectionServer for connection key \"{self.connection_key}\" is not running.", file=sys.stderr)
            sys.exit(2)

    def run(self):

        self.check_ssh_connection_server_running()

        context = zmq.Context()

        socket = context.socket(zmq.REQ)

        if not self.socket_path.exists():
            print(f"SSHConnectionServer with key \"{self.connection_key}\" does not exist", file=sys.stderr)
            sys.exit(1)

        socket.connect(f"ipc://{self.socket_path}")

        total_command = ''
        input_data = sys.stdin.read(1024)
        while len(input_data) > 0:
            total_command += input_data
            input_data = sys.stdin.read(1024)

        total_command = total_command.strip()

        if total_command == "CLOSE":
            json_data = total_command
        else:
            json_data = {
                "command": total_command
            }

        json_string = json.dumps(json_data, indent=4, sort_keys=True)
        socket.send_string(json_string)

        output_bytes = socket.recv_string()

        json_data = json.loads(output_bytes)
        
        if isinstance(json_data, str):
            print(json_data)
        else:
            print(json_data['output'], end='')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="SSHConnectionTerminalClient.py",
        description="Submit commands to an SSHConnectionServer"
    )
    parser.add_argument(
        "connection_key",
        nargs="?",
        help="Key for the SSHConnectionServer"
    )

    args = parser.parse_args()

    ssh_connection_terminal_client = SSHConnectionTerminalClient(args.connection_key)
    ssh_connection_terminal_client.run()
