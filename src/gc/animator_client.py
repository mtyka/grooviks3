'''
Created on Jun 2, 2013

@author: David
'''

import httplib
import json


class Animator:
    def __init__(self):
        self._connection = httplib.HTTPConnection('localhost', 7890)

    def animate(self, data):
        self._connection.request("POST", "/cube/display", json.dumps(data))


