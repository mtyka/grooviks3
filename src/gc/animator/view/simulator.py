import sys
import math
import Queue
from Tkinter import *

from model import cube
from spatial import *


"""
 Groovik's cube has 54 colors, arranged (at the moment) in this fashion.

 This is a right-handed coordinate system.  

 Cube coordinate system: +Z points "up", +X points "east", and +Y points "north".
 View coordinate system: +Z points toward camera, +X points "right", +Y points "up".

  EAST        WEST           NORTH         SOUTH         TOP         BOTTOM
  x = 1       x = -1         y = 1         y = -1        z = 1       z = -1
 Z           Z              Z             Z             Y            Y
 ^           ^              ^             ^             ^            ^
 |6 7 8      |15 16 17      |24 25 26     |33 34 35     |42 43 44    |51 52 53
 |3 4 5      |12 13 14      |21 22 23     |30 31 32     |39 40 41    |48 49 50
 |0 1 2      |9  10 11      |18 19 20     |27 28 29     |36 37 38    |45 46 47
  ------> Y   --------> -Y   -------> -X   --------> X   -------->X   --------> -X
"""


WINDOW_SIZE = 1000, 500
CAPTION = "Cube Console & Simulator"
FPS = 3

# border size, as percent of Side size
BORDER = 2.5            







# TkInter wrapper functions
def _geometry(size):
    return "%dx%d" % (size[0], size[1])

def _color(color):
    return "#%02x%02x%02x" % (color[0], color[1], color[2])

def _render_polygon(view, color, points):
    canvas = view.frame.canvas
    canvas.create_polygon(points, fill=_color(color))
    canvas.pack(fill=BOTH, expand=1)







class _Projection:
    def __init__(self, style, win_size, fov, viewer_position):
        self.style = style
        self.win_size = win_size
        self.fov = fov
        self.viewer_position = viewer_position


class _View:
    def __init__(self, frame, visible_sides, projection, rots=[], translation=Point(0,0,0)):
        self.frame = frame
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
        self.polygon.draw(_render_polygon, view, color)

 
class _Side:
    def __init__(self, name, rots, trans):
        self.name = name

        border = BORDER/100.0

        # Section the standard square polygon at z=1 into 9 facets
        self.facets = []
        for r in range(3):
            rA = (float(r)/3 + border)*2
            rB = (float(r+1)/3 - border)*2
            for c in range(3):
                # create polygon at Z=1 bwtween X,Y = (-1,-1) and (1,1) 
                cA = (float(c)/3 + border)*2
                cB = (float(c+1)/3 - border)*2
                polygon = Polygon([
                    Point(cA, rA, 0),
                    Point(cB, rA, 0),
                    Point(cB, rB, 0),
                    Point(cA, rB, 0)])
                polygon.translate(Point(-1, -1, 1))

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






class Simulator(Frame):
  
    def __init__(self, parent, window_size):
        Frame.__init__(self, parent)   

        self.parent = parent

        self.canvas = Canvas(self)
        self.canvas.configure(background='black')
        
        self._setup_cubes()
        self._setup_views(window_size)

        self._draw()
        self.run()

    def resize(self, event):
        window_size = event.width, event.height
        self._setup_views(window_size)
        #self.draw()


    def _setup_cubes(self):
        self.vcube3D = _VirtualCube([
            _Side('E', [Rot('Y', 90)], Point(0,0,0)),
            _Side('W', [Rot('Y', -90)], Point(0,0,0)),
            _Side('N', [Rot('X', -90)], Point(0,0,0)),
            _Side('S', [Rot('X', 90)], Point(0,0,0)),
            _Side('T', [], Point(0,0,0)),
            _Side('B', [Rot('Y', 180)], Point(0,0,0)),
            ])

        self.vcubeFlat = _VirtualCube([
            _Side('E', [], Point(0,3,0)),
            _Side('W', [], Point(0,-1,0)),
            _Side('N', [], Point(0,1,0)),
            _Side('S', [], Point(0,-3,0)),
            _Side('T', [], Point(-2,1,0)),
            _Side('B', [], Point(2,1,0)),
            ])


    def _setup_views(self, window_size):

        width = window_size[0]
        height = window_size[1]

        size = min(width/3, height)
        offset = size*95/100
        fov = size * 2

        projection3D = _Projection('3D', window_size, fov, 8)
        projectionFlat = _Projection('flat', window_size, fov, 16)

        global view1
        global view2
        global view3

        # View of East, South, and Top
        view1 = _View(
            frame = self, 
            visible_sides = ['E', 'S', 'T'],
            projection = projection3D, 
            rots = [Rot('Z', -60), Rot('X', -70)], 
            translation = Point(-offset, 0, 0)
            );
            
        # View of West, North, and Bottom
        view2 = _View(
            frame = self, 
            visible_sides = ['W', 'N', 'B'],
            projection = projection3D, 
            rots = [Rot('Z', 120), Rot('X', -105)], 
            translation = Point(0, 0, 0)
            );
            
        # Flat View
        view3 = _View(
            frame = self, 
            visible_sides = ['E', 'S', 'T', 'W', 'N', 'B'],
            projection = projectionFlat,
            rots = [],
            translation = Point(offset, 0, 0)
            );
            
    def _draw(self):
        self.canvas.delete(ALL)

        self.vcube3D.draw(view1)
        self.vcube3D.draw(view2)
        self.vcubeFlat.draw(view3)
        
        self.pack(fill=BOTH, expand=1)

    def run(self):
        # look for command on queue
        try:
            command = cube.simulator_queue.get(False)
            if (command == 'QUIT'):
                sys.exit()
            elif (command == 'DRAW'):
                self._draw()
        except Queue.Empty:
            pass

        # try again after drawing & waiting
        self.canvas.after(int(1000.0/FPS), self.run)




def run_simulation(window_size = WINDOW_SIZE):
    global view1
    global view2
    global view3

    tk = Tk()
    tk.geometry(_geometry(window_size))
    tk.title(CAPTION)        

    simulator = Simulator(tk, window_size)

    tk.bind('<Escape>', lambda event: sys.exit())
    tk.bind("<Configure>", lambda event: simulator.resize(event))
    
    tk.mainloop()  


