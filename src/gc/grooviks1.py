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
import re
from string import maketrans
from animator_client import Animator

mimerender = mimerender.WebPyMimeRender()

RESULT = 'result'

HTML_TEMPLATE = "<html><body>%s</body></html>"

render_xml = lambda **args: '<games>%s</games>' % ('<game>%s</game>' * len(args[RESULT])) % tuple(args[RESULT])
render_json = lambda **args: json.dumps(args[RESULT])
render_html = lambda **args: HTML_TEMPLATE % render_json(**args)

def mr(target):
    @mimerender(
        default = 'json',
        html = render_html,
        xml  = render_xml,
        json = render_json,
        txt  = render_json,
    )
    def wrapped(*args):
        return target(*args)
    return wrapped

MOVE_PATTERN = "(?:[LRUDFB]w?|[MESlrudfbxyz])[123']?"

# URL routing for the server
urls = (
    '/gc1/games(?:/)?', 'Games',
    '/gc1/games/(\d+)', 'Game',
    '/gc1/games/(\d+)/moves', 'Moves',
    '/gc1/games/(\d+)/moves/(\d+)/((?:%s)+)' % MOVE_PATTERN, 'Moves',
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
], 'datagram':  # BGR triplets
    "%02x%02x%02x" % (  0, 255,   0) * 9 + # R
    "%02x%02x%02x" % (255,   0,   0) * 9 + # L
    "%02x%02x%02x" % (255, 255, 255) * 9 + # F
    "%02x%02x%02x" % (  0, 255, 255) * 9 + # B
    "%02x%02x%02x" % (  0, 120, 255) * 9 + # D
    "%02x%02x%02x" % (  0,   0, 255) * 9 } # U

def _repr_cross(datagram):
    # TODO(david): Produce the 'cross' representation from the RGB datagram
    pass

def next_game():
    global _next_game_id
    game_id = _next_game_id
    _next_game_id += 1
    return { 'id': game_id, 'cube': _solved, 'moves': [] }

class Games:
    """Show all my games:
     GET /games

    Create a new game (optionally, with the given name):
     POST /games ?name=<name>

    """
    @mr
    def GET(self):
        return { RESULT: games().values() }

    @mr
    def POST(self):
        req = web.input()
        new_game = next_game()

        if ('name' not in req):
            new_game['name'] = "Game %d" % new_game['id']
        else:
            new_game['name'] = req['name']

        games()[new_game['id']] = new_game
        return { RESULT: new_game }

class Game:
    """Print the details of game 1:
     GET /games/1
      => { state: (ACTIVE|WAITING), hash: 0x140de050, cube: { format: cross, repr: [[...]] } }

    Update the state of game 1:
     PUT /games/1 { cube: { format: cross, repr: [[...]] } }

    Delete game 1:
     DELETE /games/1

    """
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
        return { RESULT: "" }

class Moves:
    def __init__(self):
        self._animator = Animator()
    
    """List all of the moves made in game 1.
     GET /games/1/moves
      => "R2u'blf'ur"

    Register move 34 in game 1:  turn the Right face 3 turns clockwise.
     PUT /games/1/moves/34/R3
     PUT /games/1/moves?new=R3&pos=34

    Register three moves (which need not all be new), starting at move 34:
     PUT /games/1/moves/34/UL2x
     PUT /games/1/moves?new=UL2x&pos=34

    Move notation grammar:
     move:
      rotation [direction]
      face [wide] [direction]

     rotation:
      "x" | "y" | "z"

     face:
      single_face
      middle_face
      double_face

     single_face:
      "L" | "R" | "U" | "D" | "F" | "B"

     middle_face:
      "M" | "E" | "S"

     double_face:
      "l" | "r" | "u" | "d" | "f" | "b"

     wide:
      "w"

     # Includes the non-standard notation extensions "1" and "3"
     direction:
      "1" | "2" | "3" | "'"

    """
    @mimerender(
        default = 'txt',
        txt = lambda **args: " ".join(args['moves']),
        json = lambda **args: json.dumps(args['moves']),
        html = lambda **args: HTML_TEMPLATE % "".join(args['moves']),
    )
    def GET(self, game_id):
        game_id = int(game_id)
        game(game_id).setdefault('moves', [])
        return game(game_id)

    @mr
    def PUT(self, game_id, move_index, new_moves):
        game_id = int(game_id)
        move_index = int(move_index)
        new_moves = new_moves.encode("ascii", "strict")
        new_moves = re.findall(MOVE_PATTERN, new_moves)
        self._record_moves(game_id, move_index, new_moves)
        return { RESULT: "" }

    def _record_moves(self, game_id, move_index, new_moves):
        """Add all of the specified moves to the game history at the given position, possibly
        overwriting existing moves.  If the given position is beyond the range currently covered by
        the game history, pad the missing moves.
        
        """
        moves = game(game_id).setdefault('moves', [])
        # If any moves have been skipped, pad the missing moves.
        moves.extend(["-"] * (move_index - len(moves) - 1))
        moves[move_index - 1:len(moves)] = [self._canonical_move(m) for m in new_moves]
        # TODO: Do this in a separate thread.
        self._animator.animate(game(game_id)['moves'])

    def _canonical_move(self, move):
        """Convert the move its canonical representation."""
        move = move.translate(maketrans("3", "'"), "1")
        match = re.match("([LRUDFB])w(.?)", move)
        if match:
            return match.group(1).lower() + match.group(2)
        else:
            return move

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
