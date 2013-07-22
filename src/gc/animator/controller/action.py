import threading
import Queue

from model import cube







def _color_cube(color):
    with cube.cube_lock:
        for i in range(54):
            cube.cube.colors[i] = color
        color = cube.cube.colors[0]







class _ActionThread(threading.Thread):
    def __init__(self):
        global animation_queue
        animation_queue = Queue.Queue(maxsize=0)
        threading.Thread.__init__(self)

    def run(self):
        while 1:
            global animation_queue
            item = animation_queue.get()
            if item is None:
                break # reached end of animation_queue
            _color_cube(item)
        print "done"










def add(color):
    global animation_queue
    animation_queue.put(color)
        

def quit():
    global animation_queue
    animation_queue.put(None)
        

def start():
    action_thread = _ActionThread()
    # This allows the web server thread to automatically quit if the program exits
    action_thread.daemon = True
    action_thread.start()
    print "running"
    time.sleep(1)
    print "add"
    print add('my color')
    time.sleep(1)
    print "quit"
    quit()







start()


