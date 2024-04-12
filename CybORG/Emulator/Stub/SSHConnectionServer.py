from typing import Union

import argparse
import json
import os
import paramiko
from pathlib import Path
import random
import re
import signal
import socket
import string
import sys
import time
import zmq


class SSHConnectionServer:

    marker_size = 10
    enable_bracketed_paste = "\x1b[?2004h"
    disable_bracketed_paste = "\x1b[?2004l\r"

    def __init__(
            self,
            connection_key: str = None,
            hostname: str = None,
            username: str = None,
            password: str = None,
            private_key_file_path: Union[str, Path] = None,
            client_port: int = 0,
            server_port: int = 22
        ):

        self.socket_path = Path(f"/tmp/ssh_connection_{connection_key}")
        self.hostname = hostname
        self.username = username
        self.password = password
        self.private_key = None if private_key_file_path is None \
            else paramiko.RSAKey.from_private_key_file(str(private_key_file_path))
        self.client_port = client_port
        self.server_port = server_port

        self.socket = None
        self.ssh_session = None
        self.interactive_shell = None

        self.shell_output_bytes = None
        self.start = None

        signal.signal(signal.SIGINT, lambda signal, frame: self.handle_interrupt())

    def handle_interrupt(self):
        self.ssh_session.close()
        sys.exit(0)

    @classmethod
    def get_marker(cls):
        return ''.join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.digits
            ) for _ in range(cls.marker_size)
        )

    def eliminate_bracketed_paste_mode(cls, value):
        return value.replace(cls.enable_bracketed_paste, '').replace(cls.disable_bracketed_paste, '')

    @staticmethod
    def get_marker_command_bytes(marker):
        return f"echo -e \"\\n{marker}\"\n".encode()

    def deploy_marker(self):
        marker = self.get_marker()
        self.interactive_shell.sendall(self.get_marker_command_bytes(marker))

        pos = -1
        while pos < 0:
            self.shell_output_bytes += self.interactive_shell.recv(4096)
            pos = self.shell_output_bytes.decode()[self.start:].find(marker)

        return marker

    def get_prompt(self):
        before_marker = self.deploy_marker()
        after_marker = self.deploy_marker()

        prompt_regex = re.compile(f"{before_marker}(.*?){after_marker}", flags=re.DOTALL)
        prompt_match = prompt_regex.search(self.shell_output_bytes.decode()[self.start:])

        prompt = self.eliminate_bracketed_paste_mode(prompt_match.group(1))[2:-2]  # GET RID OF \r\n AFTER FIRST MARKER AND BEFORE SECOND MARKER

        return prompt

    def wait_for_prompt(self, prompt):
        while not self.shell_output_bytes.decode().endswith(prompt):
            self.shell_output_bytes += self.interactive_shell.recv(4096)

    def submit_command(self, command):

        # CLEAR OUT shell_output_bytes
        self.shell_output_bytes = bytes()

        # SINGLE-QUOTE COMMAND AND EXECUTE IT USING BASH 'eval' -- THIS WAY ANY INCOMPLETE QUOTES OR
        # COMMAND-SUBSTITUTIONS ARE FLAGGED AS ERRORS INSTEAD OF CONTINUATIONS
        quoted_command = "'"
        partial_command = command
        pos = partial_command.find("'")
        while pos >= 0:
            quoted_command += "'" + partial_command[:pos] + "'" + "\"'\""
            pos += 1
            partial_command = partial_command[pos:]
            pos = partial_command.find("'", start=pos)

        quoted_command += partial_command + "'"

        self.interactive_shell.sendall(f"eval {quoted_command}\n")
        while self.interactive_shell.recv_ready():
            self.shell_output_bytes += self.interactive_shell.recv(4096)

    def send_marker_probe(self):
        marker = self.get_marker()
        marker_command_bytes = self.get_marker_command_bytes(marker)
        self.interactive_shell.sendall(marker_command_bytes)

        time.sleep(0.1)
        self.shell_output_bytes += self.interactive_shell.recv(4096)
        while self.shell_output_bytes.decode().find(marker) < 0:
            self.interactive_shell.sendall(marker_command_bytes)
            time.sleep(1)
            self.shell_output_bytes += self.interactive_shell.recv(4096)

        return marker

    def get_shell_output_text(self, marker, prompt):
        shell_output_text = self.eliminate_bracketed_paste_mode(self.shell_output_bytes.decode())
        marker_position = shell_output_text.find(marker)
        shell_output_text = shell_output_text[:marker_position]
        prompt_position = shell_output_text.rfind(prompt)
        shell_output_text = shell_output_text[:prompt_position]

        return shell_output_text

    def get_command_output(self, command=None):

        self.shell_output_bytes = bytes()
        self.start = 0

        first_prompt = self.get_prompt()
        self.wait_for_prompt(first_prompt)

        self.submit_command(command)

        marker = self.send_marker_probe()

        second_prompt = self.get_prompt()
        shell_output_text = self.get_shell_output_text(marker, second_prompt)

        return shell_output_text

    def establish_session(self):
        self.ssh_session = paramiko.SSHClient()

        self.ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("0.0.0.0", self.client_port))
        self.socket.connect((self.hostname, self.server_port))
        self.ssh_session.connect(
            hostname=self.hostname,
            password=self.password,
            pkey=self.private_key,
            username=self.username,
            sock=self.socket
        )
        self.interactive_shell = self.ssh_session.invoke_shell()
        self.interactive_shell.sendall("stty -echo\n".encode())

        shell_output_bytes = bytes()

        # BUILD THE COMMAND FOR DETERMINING WHAT THE (BASH) SHELL PROMPT LOOKS LIKE
        marker1 = self.get_marker()
        self.interactive_shell.sendall(self.get_marker_command_bytes(marker1))

        marker1_regex = re.compile(f"^{marker1}\\r$", flags=re.M)
        marker1_match = marker1_regex.search(shell_output_bytes.decode())
        while marker1_match is None:
            shell_output_bytes += self.interactive_shell.recv(4096)
            marker1_match = marker1_regex.search(shell_output_bytes.decode())

    @staticmethod
    def send_response(response, socket):
        response_json_string = json.dumps(response, indent=4, sort_keys=True)
        socket.send_string(response_json_string)

    def run(self):

        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except Exception:
                if self.socket_path.exists():
                    raise Exception(f"{self.socket_path} exists and cannot be removed in order to use it as a socket")

        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(f"ipc://{self.socket_path}")

        self.establish_session()

        while True:
            json_input = socket.recv_string()

            try:
                json_data = json.loads(json_input)

            except Exception as e:
                print(
                    f"Received input \"{json_input}\" incurred an error on parse: {str(e)}.  Ignoring",
                    file=sys.stderr
                )
                self.send_response("ERROR", socket)
                continue

            if json_data == "CLOSE":
                self.ssh_session.close()
                self.socket = None
                self.send_response("CLOSED", socket)
                socket.close()
                self.socket_path.unlink()
                return

            command = json_data["command"].strip()

            try:
                command_output = self.get_command_output(command)
                self.send_response({
                    'output': command_output
                }, socket)

            except Exception as e:
                try:
                    self.ssh_session.close()

                    self.socket = None
                except Exception:
                    pass

                self.establish_session()
                self.send_response("RECONNECT", socket)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="SSHConnection.py",
        description="Server for communicating over a persistent SSH connection"
    )
    parser.add_argument(
        "-n", "--connection-key", required=True,
        help="key used to unique identify ssh connection"
    )
    parser.add_argument(
        "-m", "--hostname", required=True,
        help="name or ip-address of host to which to connect"
    )
    parser.add_argument(
        "-u", "--username", action="store", required=True,
        help="name of user for SSH connection"
    )
    password_key_group = parser.add_mutually_exclusive_group(required=True)
    password_key_group.add_argument(
        "-k", "--private-key-file", action="store", required=False,
        help="path of private RSA key file to be used for the SSH connection"
    )
    password_key_group.add_argument(
        "-p", "--password", action="store", required=False,
        help="password of user"
    )
    parser.add_argument(
        "-d", "--daemon", action="store_true", help="make server a daemon"
    )
    parser.add_argument(
        "-c", "--client-port", action="store", required=False, default=0, type=int,
        help="client port for ssh connection (default = 0 (random port))"
    )
    parser.add_argument(
        "-s", "--server-port", action="store", required=False, default=22, type=int,
        help="server port for ssh connection"
    )

    args = parser.parse_args()

    if args.daemon:
        pid = os.fork()
        if pid < 0:
            sys.exit(1)

        if pid > 0:
            sys.exit(0)

        os.setsid()
        os.chdir("/")
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()

    ssh_connection = SSHConnectionServer(
        connection_key=args.connection_key,
        hostname=args.hostname,
        username=args.username,
        password=args.password,
        private_key_file_path=args.private_key_file,
        client_port=args.client_port,
        server_port=args.server_port
    )

    ssh_connection.run()
