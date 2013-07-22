import threading
import Queue
from model import cube
from view import simulator
from controller import web_server
#from controller import action




def main():
    # Action command queue
#    action.start()
    
    # Web Server
    web_server.start()

    # Simulator View
    simulator.run_simulation()


if __name__ == "__main__":
    main()


