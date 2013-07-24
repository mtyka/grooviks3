'''
Created on Jun 2, 2013

@author: David, Geoff
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
        # TODO(geoff): animate wants cube state (colors), not moves
#        self._connection.request("POST", "/animator/actions", json.dumps(data))

        message = {
            'datagram':
                9 * _COLOR_GREEN +  # R
                9 * _COLOR_BLUE +   # L
                9 * _COLOR_WHITE +  # F
                9 * _COLOR_YELLOW + # B
                9 * _COLOR_ORANGE + # D
                9 * _COLOR_RED      # U
            }

        self._connection.request("POST", "/animator/actions", "ff0044")

    def quit(self):
        self._connection.request("DELETE", "/animator")


    
