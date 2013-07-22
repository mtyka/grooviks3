import re
from string import maketrans


# Wacky custom representation of cube.  This view show the cube as if it were
# unfolded into the shape of a cross, with the literal colors of the facets
# recorded at each location.  The 3x3 square at the center of the cross is the
# front of the cube (i.e. the "F" face, in Singmaster notation); the right and
# left arms are R and L, respectively, the top arm is U, and the bottom arm is
# D (down) then B (back) at the bottom.
#
# TODO(david): see if we can find a more standard representation 
_solved = { 
    'format': 'cross', 
    'repr': [ 
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
        ], 
    'datagram':  # BGR triplets
        "%02x%02x%02x" % (  0, 255,   0) * 9 + # R
        "%02x%02x%02x" % (255,   0,   0) * 9 + # L
        "%02x%02x%02x" % (255, 255, 255) * 9 + # F
        "%02x%02x%02x" % (  0, 255, 255) * 9 + # B
        "%02x%02x%02x" % (  0, 120, 255) * 9 + # D
        "%02x%02x%02x" % (  0,   0, 255) * 9 # U
    }

def _repr_cross(datagram):
    # TODO(david): Produce the 'cross' representation from the RGB datagram
    pass






_games = {}
_id_cur = 0

def games():
    return _games

def game(game_id):
    return _games.setdefault(game_id, {})

def add(name = None):
    global _id_cur 
    _id_cur += 1

    if not name:
        name = "Game %d" % _id_cur
        
    _games[_id_cur] = {
        'id': _id_cur, 
        'name': name,
        'cube': _solved,
        'moves': [],
        }

# TODO: Separate out Moves object
def record_moves(game_id, move_index, new_moves):
    """Add all of the specified moves to the game history at the given position, possibly
    overwriting existing moves.  If the given position is beyond the range currently covered by
    the game history, pad the missing moves.
    
    """
    moves = _games[game_id].setdefault('moves', [])
    # If any moves have been skipped, pad the missing moves.
    moves.extend(["-"] * (move_index - len(moves) - 1))
    moves[move_index - 1:len(moves)] = [_canonical_move(m) for m in new_moves]

def _canonical_move(move):
    """Convert the move its canonical representation."""
    move = move.translate(maketrans("3", "'"), "1")
    match = re.match("([LRUDFB])w(.?)", move)
    if match:
        return match.group(1).lower() + match.group(2)
    else:
        return move









