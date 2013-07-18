'''
Created on Mar 16, 2013.

This server simulates a simple single player Rubik's Cube game session.  It
simply allows clients to create games and to update the server with the state
of their local game.

Instructions to run:

  # In one window:
  python gc/animator.py 7890
  
  # In a second one:  
  python gc/server.py <port>

@author: David, Geoff
'''

from controller import web_server




def main():
    web_server.ws_run()


if __name__ == '__main__':
    main()



