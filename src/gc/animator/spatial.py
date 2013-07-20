import math


class Rot:
    def __init__(self, axis, angle):
        assert axis in ['X', 'Y', 'Z']
        self.axis = axis
        self.angle = angle
    

class Point:
    def __init__(self, x=0.0, y=0.0, z=0):
        self.x, self.y, self.z = float(x), float(y), float(z)

    def dump(self):
        print self.x, self.y, self.z

    def copy(self):
        return Point(self.x, self.y, self.z)

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


class Polygon:
    def __init__(self, points):
        self.points = points

    def dump(self):
        for point in self.points:
            point.dump()
        print

    def copy(self):
        points = []
        for point in self.points:
            points.append(Point(point.x, point.y, point.z))
        return Polygon(points)

    def rotate(self, rot):
        for point in self.points:
            point.rotate(rot)

    def translate(self, vec):
        for point in self.points:
            point.translate(vec)
    
    def project(self, projection):
        for point in self.points:
            point.project(projection)

    def draw(self, fn, view, color):
        polygon = self.copy()

        for rot in view.rots:
            polygon.rotate(rot)

        polygon.project(view.projection)
        polygon.translate(view.translation)

        poly2d = []
        for point in polygon.points:
            poly2d.append((point.x, point.y))

        fn(view.screen, color, poly2d, 0)


