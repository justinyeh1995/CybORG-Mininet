import pexpect
import traceback 
import inspect
import logging

from CybORG import CybORG, CYBORG_VERSION
from CybORG.Mininet.mininet_adapter.entity import Entity

class MininetCommandInterface(Entity):
    def __init__(self):
        self.mininet_process = None
        
    
    def start_mininet(self, topology_file: str) -> str:
        try:
            logging.info ("Starting Mininet network topology")
            path = str(inspect.getfile(CybORG))
            path = path[:-10] + f'/Mininet/mininet_api/custom_net.py' # To-Do: might need to be configurable in the config file
            self.mininet_process = pexpect.spawn(f"sudo python3 {path} -y {topology_file}")
            self.mininet_process.timeout = 300
            self.mininet_process.expect("mininet>")
            return self.mininet_process.before.decode()
        except Exception as e:
            logging.error (f"Failed to start Mininet: {e}")
            traceback.print_exc()

    
    def send_command(self, command: str, expect_prompt: bool=True) -> str:
        if self.mininet_process and self.mininet_process.isalive():
            self.mininet_process.sendline(command)
            if expect_prompt:
                self.mininet_process.expect('mininet>')
            return self.mininet_process.before.decode()
        return "Mininet process is not running."

    
    def stop_mininet(self) -> None:
        if self.mininet_process and self.mininet_process.isalive():
            self.mininet_process.sendline('exit')
            self.mininet_process.expect(pexpect.EOF)
            logging.info ("Terminated the ongoing Mininet topology.")


    def clean(self) -> None:
        # First, ensure that the existing Mininet subprocess is terminated
        try:
            # First, check if a Mininet process is running and terminate it
            self.stop_mininet()
            
            # Now, run the Mininet cleanup command
            cleanup_process = pexpect.spawn("sudo mn -c")
            cleanup_process.timeout = 60
            cleanup_process.expect(pexpect.EOF)  # Wait for the end of the process
            logging.info ("Mininet cleaned up successfully.")
        except Exception as e:
            logging.error (f"Error cleaning up Mininet: {e}")

        finally:
            if cleanup_process is not None and cleanup_process.isalive():
                cleanup_process.terminate()