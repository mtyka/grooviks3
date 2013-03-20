'''
Created on Mar 16, 2013.

This server simulates a simple single player Rubik's Cube game session.  It
simply allows clients to create games and to update the server with the state
of their local game.

Instructions to run:

  python gc/grooviks1.py <port>

@author: David
'''

import web
import json
import mimerender

mimerender = mimerender.WebPyMimeRender() 

RESULT = 'result'

render_xml = lambda **args: '<games>%s</games>' % ('<game>%s</game>' * len(args[RESULT])) % tuple(args[RESULT])
render_json = lambda **args: json.dumps(args[RESULT])
render_html = lambda message: '<html><body>%s</body></html>'%message
render_txt = lambda message: message

def mr(target):
    @mimerender(
                default = 'json',
        html = render_html,
        xml  = render_xml,
        json = render_json,
        txt  = render_txt,
    )
    def wrapped(*args):
        return target(*args)
    return wrapped

# URL routing for the server
urls = (
    '/gc1/games(/)?', 'Games',
    '/gc1/games/(\d+)', 'Game',
)
app = web.application(urls, globals())

# Global state.
# TODO(david): replace with something more persistent, or at least shared
#  between server instances.
_next_game_id = 1
_games = {}

def games():
    return _games

def game(game_id):
    return _games[game_id]

# Wacky custom representation of cube.  This view show the cube as if it were
# unfolded into the shape of a cross, with the literal colors of the facets
# recorded at each location.  The 3x3 square at the center of the cross is the
# front of the cube (i.e. the "F" face, in Singmaster notation); the right and
# left arms are R and L, respectively, the top arm is U, and the bottom arm is
# D (down) then B (back) at the bottom.
#
# TODO(david): see if we can find a more standard representation 
_solved = { 'format': 'cross', 'repr': [ 
	'   rrr   ',
	'   rrr   ',
	'   rrr   ',
	'bbbwwwggg',
	'bbbwwwggg',
	'bbbwwwggg',
	'   ooo   ',
	'   ooo   ',
	'   ooo   ',
	'   yyy   ',
	'   yyy   ',
	'   yyy   ',
] }

def next_game():
    global _next_game_id
    game_id = _next_game_id
    _next_game_id += 1
    return { 'id': game_id, 'cube': _solved }

#
# GET /games
# POST /games ?name=<name>
#
class Games:
    @mr
    def GET(self, _):
        return { RESULT: games().values() }
    
    @mr
    def POST(self, _):
        req = web.input()
        new_game = next_game()
        
        if ('name' not in req):
            new_game['name'] = "Game %d" % new_game['id']
        else:
            new_game['name'] = req['name']
        
        games()[new_game['id']] = new_game
        return { RESULT: new_game }

#
# GET /games/1 => { state: (ACTIVE|WAITING), hash: 0x140de050, cube: { format: cross, repr: [[...]] } }
# PUT /games/1 { hash: 0x140de050, move: "R'" } # idempotent
# PUT /games/1 { cube: { format: cross, repr: [[...]] } } # idempotent
# DELETE /games/1
#
class Game:
    @mr
    def GET(self, game_id):
        game_id = int(game_id)
        return { RESULT: game(int(game_id)) }
    
    @mr
    def PUT(self, game_id):
        game_id = int(game_id)
        if (len(web.data()) > 0):
            # TODO(david): parse based on Content-Type
            req = json.loads(web.data())
            if ('cube' in req):
                # TODO(david): validate that the new cube state is legal
                game(game_id)['cube'] = req['cube']
        return { RESULT: game(int(game_id)) }
    
    @mr
    def DELETE(self, game_id):
        game_id = int(game_id)
        del games()[game_id]

#
# GET /admin
#
class Admin:
    # TODO
    pass

#
# API for adding physical cubes to the game server so that they may be attached
# to games.
#
# GET /cubes
# POST /cubes { physical cube self-registration }
#
class Cubes:
    # TODO
    pass

if __name__ == '__main__':
    app.run()
