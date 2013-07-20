import sys
import math
import pygame

from model import cube


"""
 Groovik's vcube3D has 54 colors, arranged (at the moment) in this fashion.

 This is a right-handed coordinate system.  

 _VirtualCube coordinate system: +Z points "up", +X points "east", and +Y points "north".
 _View coordinate system: +Z points toward camera, +X points "right", +y points "up".

  EAST        WEST           NORTH         SOUTH         TOP         BOTTOM
  x = 1       x = -1         y = 1         y = -1        z = 1       z = -1
 Z           Z              Z             Z             Y            Y
 ^           ^              ^             ^             ^            ^
 |6 7 8      |15 16 17      |24 25 26     |33 34 35     |42 43 44    |51 52 53
 |3 4 5      |12 13 14      |21 22 23     |30 31 32     |39 40 41    |48 49 50
 |0 1 2      |9  10 11      |18 19 20     |27 28 29     |36 37 38    |45 46 47
  ------> Y   --------> -Y   -------> -X   --------> X   -------->X   --------> -X
"""


class _Rot:
    def __init__(self, axis, angle):
        assert axis in ['X', 'Y', 'Z']
        self.axis = axis
        self.angle = angle
    

class _Point:
    def __init__(self, x=0.0, y=0.0, z=0):
        self.x, self.y, self.z = float(x), float(y), float(z)

    def dump(self):
        print self.x, self.y, self.z

    def copy(self):
        return _Point(self.x, self.y, self.z)

    def rotate(self, rot):
        rad = rot.angle * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        if rot.axis == 'X':
            x = self.x
            y = self.y * cosa - self.z * sina
            z = self.y * sina + self.z * cosa
        elif rot.axis == 'Y':
            x = self.z * sina + self.x * cosa
            y = self.y
            z = self.z * cosa - self.x * sina
        elif rot.axis == 'Z':
            x = self.x * cosa - self.y * sina
            y = self.x * sina + self.y * cosa
            z = self.z
        else:
            raise Exception("bogus axis")
        self.x = x
        self.y = y
        self.z = z
 
    def translate(self, vec):
        self.x += vec.x
        self.y += vec.y
        self.z += vec.z
 
    def project(self, projection):
        """ Transforms this 3D point to 2D using a perspective projection. """
        factor = projection.fov / (projection.viewer_position - self.z)
        self.x = self.x * factor + projection.win_size[0] / 2
        self.y = -self.y * factor + projection.win_size[1] / 2


class _Polygon:
    def __init__(self, points):
        self.points = points

    def dump(self):
        for point in self.points:
            point.dump()
        print

    def copy(self):
        points = []
        for point in self.points:
            points.append(_Point(point.x, point.y, point.z))
        return _Polygon(points)

    def rotate(self, rot):
        for point in self.points:
            point.rotate(rot)

    def translate(self, vec):
        for point in self.points:
            point.translate(vec)
    
    def project(self, projection):
        for point in self.points:
            point.project(projection)

    def draw(self, view, color):
        polygon = self.copy()

        for rot in view.rots:
            polygon.rotate(rot)

        polygon.project(view.projection)
        polygon.translate(view.translation)

        poly2d = []
        for point in polygon.points:
            poly2d.append((point.x, point.y))

        pygame.draw.polygon(view.screen, color, poly2d, 0)


class _Projection:
    def __init__(self, style, win_size, fov=700, viewer_position=10):
        self.style = style
        self.win_size = win_size
        self.fov = fov
        self.viewer_position = viewer_position


class _View:
    def __init__(self, screen, visible_sides, projection, rots=[], translation=_Point(0,0,0)):
        self.screen = screen
        self.visible_sides = visible_sides
        self.projection = projection
        self.rots = rots
        self.translation = translation


class _Facet:
    def __init__(self, side, r, c, polygon):
        self.side = side
        self.r = r
        self.c = c
        self.polygon = polygon

    def draw(self, view):
        with cube.cube_lock:
            color = cube.cube.facet_color(self.side, self.r, self.c)
        self.polygon.draw(view, color)

 
class _Side:
    def __init__(self, name, rots, trans, border=0.025):
        self.name = name
        self.border = border

        # Section the standard square polygon at z=1 into 9 facets
        self.facets = []
        for r in range(3):
            rA = (float(r)/3 + self.border)*2
            rB = (float(r+1)/3 - self.border)*2
            for c in range(3):
                # create polygon at Z=1 bwtween X,Y = (-1,-1) and (1,1) 
                cA = (float(c)/3 + self.border)*2
                cB = (float(c+1)/3 - self.border)*2
                polygon = _Polygon([
                    _Point(cA, rA, 0),
                    _Point(cB, rA, 0),
                    _Point(cB, rB, 0),
                    _Point(cA, rB, 0)])
                polygon.translate(_Point(-1, -1, 1))

                # apply rotations to put side into place
                for rot in rots:
                    polygon.rotate(rot)
                polygon.translate(trans)
                self.facets.append(_Facet(name, r, c, polygon))
            
    def dump(self):
        print "_Facet "+self.name
        for facet in self.facets:
            facet.dump()

    def draw(self, view)  :
        for facet in self.facets:
            facet.draw(view)


class _VirtualCube:
    def __init__(self, sides):
        self.sides = sides
       
    def draw(self, view):
        for side in self.sides:
            if (side.name in view.visible_sides):
                side.draw(view)




def setup_views(screen):

    width = screen.get_width()
    height = screen.get_height()
    size = min(width/3, height)
    fov = size * 2

    projection3D = _Projection('3D', screen.get_size(), fov, 8)
    projectionFlat = _Projection('flat', screen.get_size(), fov, 16)

    global view1
    global view2
    global view3

    # _View of East, South, and Top
    view1 = _View(
        screen = screen, 
        visible_sides = ['E', 'S', 'T'],
        projection = projection3D, 
        rots = [_Rot('Z', -60), _Rot('X', -70)], 
        translation = _Point(-size, 0, 0)
        );
        
    # _View of West, North, and Bottom
    view2 = _View(
        screen = screen, 
        visible_sides = ['W', 'N', 'B'],
        projection = projection3D, 
        rots = [_Rot('Z', 120), _Rot('X', -105)], 
        translation = _Point(0, 0, 0)
        );
        
    # Flat _View
    view3 = _View(
        screen = screen, 
        visible_sides = ['E', 'S', 'T', 'W', 'N', 'B'],
        projection = projectionFlat,
        rots = [],
        translation = _Point(size, 0, 0)
        );



def run_simulation(resolution = (1000, 500), fps = 30):
    global view1
    global view2
    global view3

    pygame.init()
    pygame.display.set_caption("_VirtualCube Console & Simulator")

    screen = pygame.display.set_mode(resolution, pygame.RESIZABLE)
    
    clock = pygame.time.Clock()

    vcube3D = _VirtualCube([
        _Side('E', [_Rot('Y', 90)], _Point(0,0,0)),
        _Side('W', [_Rot('Y', -90)], _Point(0,0,0)),
        _Side('N', [_Rot('X', -90)], _Point(0,0,0)),
        _Side('S', [_Rot('X', 90)], _Point(0,0,0)),
        _Side('T', [], _Point(0,0,0)),
        _Side('B', [_Rot('Y', 180)], _Point(0,0,0)),
        ])

    vcubeFlat = _VirtualCube([
        _Side('E', [], _Point(0,3,0)),
        _Side('W', [], _Point(0,-1,0)),
        _Side('N', [], _Point(0,1,0)),
        _Side('S', [], _Point(0,-3,0)),
        _Side('T', [], _Point(-2,1,0)),
        _Side('B', [], _Point(2,1,0)),
        ])

    setup_views(screen)

    """ Main Loop """
    try:
        while 1:

            for event in pygame.event.get():
                if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)
                    setup_views(screen)

            clock.tick(fps)
            screen.fill((0,0,0))

            vcube3D.draw(view1)
            vcube3D.draw(view2)
            vcubeFlat.draw(view3)
            
            pygame.display.flip()

    # Let control-C from the console quietly stop us
    except (KeyboardInterrupt, SystemExit):
        sys.exit()




