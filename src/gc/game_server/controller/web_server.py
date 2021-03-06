import web
import json
import mimerender
import re
import sys

from model import games 
from view import animator




MOVE_PATTERN = "(?:[LRUDFB]w?|[MESlrudfbxyz])[123']?"

# URL routing for the server
URLS = (
    '/gc', '_REST',
    '/gc/games(?:/)?', '_REST_Games',
    '/gc/games/(\d+)', '_REST_Game',
    '/gc/games/(\d+)/moves', '_REST_Moves',
    '/gc/games/(\d+)/moves/(\d+)/((?:%s)+)' % MOVE_PATTERN, '_REST_Moves',
)





animator = animator.Animator()

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




class _REST:
    """Take down server:
     DELETE /gc

    """
    def DELETE(self):
        print "Cube Game Server shutting down..."
        animator.quit()
        sys.exit()



class _REST_Games:
    """Show all my games:
     GET /gc/games

    Create a new game (optionally, with the given name):
     POST /gc/games ?name=<name>

    """
    @mr
    def GET(self):
        return { RESULT: games.games().values() }

    @mr
    def POST(self):
        req = web.input()
        name = req.get('name', None)
        game_id = games.add(name)
        return { RESULT: game_id }



class _REST_Game:
    """Print the details of game 1:
     GET /gc/games/1
      => { state: (ACTIVE|WAITING), hash: 0x140de050, cube: { format: cross, repr: [[...]] } }

    Update the state of game 1:
     PUT /gc/games/1 { cube: { format: cross, repr: [[...]] } }

    Delete game 1:
     DELETE /gc/games/1

    """
    @mr
    def GET(self, game_id):
        game_id = int(game_id)
        return { RESULT: games.game(game_id) }

    @mr
    def PUT(self, game_id):
        game_id = int(game_id)
        if (len(web.data()) > 0):
            # TODO(david): parse based on Content-Type
            req = json.loads(web.data())
            if ('cube' in req):
                # TODO(david): validate that the new cube state is legal
                games.game(game_id)['cube'] = req['cube']
        return { RESULT: games.game(game_id) }

    @mr
    def DELETE(self, game_id):
        game_id = int(game_id)
        del games._games[game_id]
        return { RESULT: "" }



class _REST_Moves:
    
    """List all of the moves made in game 1.
     GET /gc/games/1/moves
      => "R2u'blf'ur"

    Register move 34 in game 1:  turn the Right face 3 turns clockwise.
     PUT /gc/games/1/moves/34/R3
     PUT /gc/games/1/moves?new=R3&pos=34

    Register three moves (which need not all be new), starting at move 34:
     PUT /gc/games/1/moves/34/UL2x
     PUT /gc/games/1/moves?new=UL2x&pos=34

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
        print games.game(game_id)
        return games.game(game_id)

    @mr
    def PUT(self, game_id, move_index, new_moves):
        game_id = int(game_id)
        move_index = int(move_index)
        new_moves = new_moves.encode("ascii", "strict")
        new_moves = re.findall(MOVE_PATTERN, new_moves)
        games.record_moves(game_id, move_index, new_moves)
        animator.animate(games.game(game_id)['moves'])
        return { RESULT: "" }





#
# GET /admin
#
class _REST_Admin:
    # TODO
    pass



#
# API for adding physical cubes to the game server so that they may be attached
# to games.
#
# GET /cubes
# POST /cubes { physical cube self-registration }
#
class _REST_Cubes:
    # TODO
    pass





def ws_run():
    app = web.application(URLS, globals())
    app.run()
    

