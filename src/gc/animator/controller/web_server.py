import web
import json
import mimerender
import re
import threading

from model import cube




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
    '/cube/animate', '_AnimateREST',
)



class _AnimateREST:
    @mr
    def POST(self):
        if len(web.data()) == 0:
            raise Exception('No data')

        req = web.data()
        color = _color_from_hex(req)

        with cube.cube_lock:
            for i in range(54):
                cube.cube.colors[i] = color
            color = cube.cube.colors[0]
        
        return {}





class WebThread(threading.Thread):
    def run(self):
        app = web.application(URLS, globals())
        app.run()
      

