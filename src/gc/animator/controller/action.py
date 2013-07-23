import sys
import threading
import Queue

from model import cube
from view import simulator





queue = Queue.Queue()



def _color_cube(color):
    with cube.cube_lock:
        for i in range(54):
            cube.cube.colors[i] = color
        color = cube.cube.colors[0]




class _ActionThread(threading.Thread):
    def run(self):
        while True:
            try:
                # wait for command from queue
                item = queue.get(True)
                command = item['command']

                if (command == 'QUIT'):
                    simulator.queue.put('QUIT')

                elif (command == 'COLOR'):
                    _color_cube(item['color'])
                    simulator.queue.put('DRAW')

            except Queue.Empty:
                pass




def add(color):
    global queue
    queue.put({'command': 'COLOR', 'color': color})
        

def quit():
    global queue
    queue.put({'command': 'QUIT'})
        

def start():
    action_thread = _ActionThread()
    # This allows the web server thread to automatically quit if the program exits
    action_thread.daemon = True
    action_thread.start()



