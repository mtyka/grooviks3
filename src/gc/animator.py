'''
Created on Jun 2, 2013

@author: David
'''

import web
import json
import mimerender

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

urls = (
    '/cube/display', 'Display',
)
app = web.application(urls, globals())

class Display:
    """Basic animator service.  For now, simply echoes request arguments to
    stdout.
    
    """
    @mr
    def POST(self):
        if len(web.data()) == 0:
            raise Exception('No data')
        req = json.loads(web.data())
        print req
        return {}

if __name__ == '__main__':
    app.run()
