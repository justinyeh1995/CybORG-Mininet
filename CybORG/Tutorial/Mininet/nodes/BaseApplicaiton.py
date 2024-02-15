import sys    # for syspath and system exception
import time   # for sleep
import zmq  # ZMQ sockets
import asyncio # a concurrency model known as a single-threaded event loop
import traceback

from utils import parseCmdLineArgs

class BaseAppln:
    def __init__(self, logger):
        self.logger = logger
        self.ip_addr = None
        self.port = None
        self.action = None
        
    def configure(self, arg):
        pass

    def send(self):
        pass

    def recv(self):
        pass

    def event_loop(self):
        pass
        
    def run(self):
        pass
        

def main():
    try:
        # obtain a system wide logger and initialize it to debug level to begin with
        logging.debug ("Main - acquire a child logger and then log messages in the child")
        logger = logging.getLogger ("BaseAppln")
        
        # first parse the arguments
        logger.debug ("Main: parse command line arguments")
        args = parseCmdLineArgs ()
        
        # reset the log level to as specified
        logger.debug ("Main: resetting log level to {}".format (args.loglevel))
        logger.setLevel (args.loglevel)
        logger.debug ("Main: effective log level is {}".format (logger.getEffectiveLevel ()))
        
        # Obtain a publisher application
        logger.debug ("Main: obtain the object")
        pub_app = BaseAppln (logger)
        
        # configure the object
        pub_app.configure (args)
        # now invoke the driver program
        pub_app.driver ()
    
    except Exception as e:
        logger.error ("Exception caught in main - {}".format (e))
        return

if __name__ == "__main__":

    # set underlying default logging capabilities
    logging.basicConfig (level=logging.DEBUG,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    

    main()