#!/usr/bin/python3

from typing import Union

import argparse
import os
import paramiko
from pathlib import Path
import signal
import socket
import sys

from CybORG.Mininet.systems.scripts.ShellRelayer import ShellRelayer


class SSHConnectionServer:

    pid_directory = Path("/", "usr", "local", "run")

    def __init__(
            self,
            connection_key: str = None,
            hostname: str = None,
            username: str = None,
            password: str = None,
            private_key_file_path: Union[str, Path] = None,
            client_port: int = 0,
            server_port: int = 22,
            is_daemon: bool = False
    ):

        self.connection_key = connection_key

        self.shell_relayer = ShellRelayer(connection_key)

        self.hostname = hostname
        self.username = username
        self.password = password
        self.private_key = None if private_key_file_path is None \
            else paramiko.RSAKey.from_private_key_file(str(private_key_file_path))
        self.client_port = client_port
        self.server_port = server_port

        self.is_daemon = is_daemon
        self.daemon_incomplete = True

        self.socket = None
        self.ssh_session = None
        self.interactive_shell = None

        self.shell_output_bytes = None
        self.start = None

        signal.signal(signal.SIGINT, lambda signal, frame: self.handle_interrupt())

    def handle_interrupt(self):
        self.ssh_session.close()
        sys.exit(0)

    def establish_session(self):
        self.ssh_session = paramiko.SSHClient()

        self.ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("0.0.0.0", self.client_port))
        self.socket.connect((self.hostname, self.server_port))
    

    def check_daemon(self):
        if self.daemon_incomplete:

            if self.is_daemon:
                pid = os.fork()
                if pid < 0:
                    print("Could not fork in daemon mode")
                    sys.exit(1)

                if pid > 0:
                    os.close(self.socket.fileno())
                    print("SSHConnectionServer daemon running (has socket connection).")
                    sys.exit(0)

                os.setsid()
                os.chdir("/")
                os.close(0)
                os.close(1)
                os.close(2)

            pid_file_path = Path(self.pid_directory, f"SSHConnectionServer_{self.connection_key}.pid")
            with pid_file_path.open("w") as output_fd:
                print(os.getpid(), file=output_fd)
            
            self.daemon_incomplete = False

            self.ssh_session.connect(
                hostname=self.hostname,
                password=self.password,
                pkey=self.private_key,
                username=self.username,
                sock=self.socket
            )
            self.interactive_shell = self.ssh_session.invoke_shell()
            print(self.interactive_shell)

    def run(self):

        while True:
            try:
                self.establish_session()

                self.check_daemon()

                self.shell_relayer.run(self.interactive_shell, "RECONNECT")
                return

            except OSError as oserror:
                if oserror.errno is None:
                    pass
                else:
                    print(f"OSError #{oserror.errno}: {oserror.strerror}")
                    sys.exit(1)

            except Exception as e:
                pass

            self.ssh_session.close()
            self.daemon_incomplete = True
            self.is_daemon = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="SSHConnectionServer.py",
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

    ssh_connection = SSHConnectionServer(
        connection_key=args.connection_key,
        hostname=args.hostname,
        username=args.username,
        password=args.password,
        private_key_file_path=args.private_key_file,
        client_port=args.client_port,
        server_port=args.server_port,
        is_daemon=args.daemon
    )

    ssh_connection.run()
