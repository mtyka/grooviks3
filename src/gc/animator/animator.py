import threading
from model import cube
from view import simulator
from controller import web_server




def main():
    # Web Server
    web_thread = web_server.WebThread()
    # This allows the web server thread to automatically quit if the program exits
    web_thread.daemon = True
    web_thread.start()

    # Simulator View
    simulator.run_simulation()


if __name__ == "__main__":
    main()


