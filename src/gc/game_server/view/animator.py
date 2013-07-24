'''
Created on Jun 2, 2013

@author: David
'''

import httplib
import json


class Animator:
    """Basic client for animator service (animator.py).
    
    This client simply converts unstructured data to JSON and sends it to the
    service.  It is hardcoded, presently, to localhost:7890.
    
    """
    def __init__(self):
        self._connection = httplib.HTTPConnection('localhost', 7890)

    def animate(self, data):
        print "animate data:", data
        print "animate data (json.dumps):", json.dumps(data)
#        self._connection.request("POST", "/animator/enqueue", json.dumps(data))
        self._connection.request("POST", "/animator/enqueue", "ff0044")


