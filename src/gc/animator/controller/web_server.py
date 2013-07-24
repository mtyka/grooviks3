import web
import json
import mimerender
import re
import threading
import Queue
import sys

import action
from model import cube
from controller import action



def _color_from_hex(hexstring):
    _re_hex = re.compile(r'([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})')
    r = _re_hex.search(hexstring).groups()
    return (int(r[0],16), int(r[1],16), int(r[2],16))





mimerender = mimerender.WebPyMimeRender()

render_json = lambda **args: json.dumps(args)

def mr(target):
    @mimerender(
        default = 'json',
        json = render_json,
    )
    def wrapped(*args):
        return target(*args)
    return wrapped

URLS = (
    '/animator', '_REST',
    '/animator/actions', '_REST_Actions',
)



class _REST:
    """ Take down server:
     DELETE /animator

    """
    @mr
    def DELETE(self):
        action.quit()
        return {}



class _REST_Actions:
    """ Queue up an animator action command
     POST /animator/actions

    """
    @mr
    def POST(self):
        if len(web.data()) == 0:
            raise Exception('No data')

        req = web.data()
        color = _color_from_hex(req)
        action.add(color)
        return {}





class _WebThread(threading.Thread):
    def run(self):
        app = web.application(URLS, globals())
        app.run()
      



def start():
    web_thread = _WebThread()
    # This allows the web server thread to automatically quit if the program exits
    web_thread.daemon = True
    web_thread.start()



