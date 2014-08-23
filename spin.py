import pyglet
from pyglet.gl import *
import math

from cube import *

def _iter_ellipse(x1, y1, x2, y2, da=None, step=None, dashed=False):
    xrad = abs((x2-x1) / 2.0)
    yrad = abs((y2-y1) / 2.0)
    x = (x1+x2) / 2.0
    y = (y1+y2) / 2.0
  
    if da and step:
        raise ValueError("Can only set one of da and step")
  
    if not da and not step:
        step = 8.0
  
    if not da:
        # use the average of the radii to compute the angle step
        # shoot for segments that are 8 pixels long
        step = 32.0
        rad = max((xrad+yrad)/2, 0.01)
        rad_ = max(min(step / rad / 2.0, 1), -1)
  
        # but if the circle is too small, that would be ridiculous
        # use pi/16 instead.
        da = min(2 * math.asin(rad_), math.pi / 16)
  
    a = 0.0
    while a <= math.pi * 2:
        yield (x + math.cos(a) * xrad, y + math.sin(a) * yrad)
        a += da
        if dashed: a += da

def ellipse(x1, y1, x2, y2):
    points = _concat(_iter_ellipse(x1, y1, x2, y2))
    pyglet.graphics.draw(len(points)/2, pyglet.gl.GL_TRIANGLE_FAN, ('v2f', points))
  
def ellipse_outline(x1, y1, x2, y2):
    points = _concat(_iter_ellipse(x1, y1, x2, y2))
    pyglet.graphics.draw(len(points)/2, pyglet.gl.GL_LINE_LOOP, ('v2f', points))
  
def _concat(it):
    return list(y for x in it for y in x)

def line(x1, y1, x2, y2, colors=None):
    if colors is None:
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (x1, y1, x2, y2)))
    else:
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (x1, y1, x2, y2)), ('c4f', colors))

from itertools import chain
from pyglet.graphics import Batch
from pyglet.graphics import vertex_list
from pyglet.gl import GL_TRIANGLE_STRIP

class Primitive(object):
    """
    Stores a list of vertices, a single color, and a primitive type
    Intended to be rendered as a single OpenGL primitive
    """
    def __init__(self, verts, color, primtype=GL_TRIANGLE_STRIP):
        self.verts = verts
        self.color = color
        self.primtype = primtype
        self.vertex_list = None
        self.flat_verts = None

    def offset(self, dx, dy):
        newverts = [(v[0] + dx, v[1] + dy) for v in self.verts]
        return Primitive(newverts, self.color, primtype=self.primtype)

    def get_flat_verts(self):
        if self.flat_verts is None:
            self.flat_verts = \
                list(self.verts[0]) + \
                [x for x in chain(*self.verts)] + \
                list(self.verts[-1])
        return self.flat_verts

    def get_vertexlist(self):
        if self.vertex_list is None:
            flatverts = self.get_flat_verts()
            numverts = len(flatverts) / 2
            self.vertex_list = vertex_list(
                numverts,
                ('v2f/static', flatverts),
                ('c3B/static', self.color * numverts))
        return self.vertex_list

class Shape(object):
    "A list of primitives"

    def __init__(self, items=None):
        self.primitives = []
        if items:
            self.add_items(items)
        self.batch = None

    def add_items(self, items):
        "Add a list of primitives and shapes"
        for item in items:
            if isinstance(item, Shape):
                self.add_shape(item)
            else:
                self.primitives.append(item)

    def add_shape(self, other):
        "Add the primitives from a given shape"
        for prim in other.primitives:
            self.primitives.append(prim)

    def get_batch(self):
        if self.batch is None:
            self.batch = Batch()
            for primitive in self.primitives:
                flatverts = primitive.get_flat_verts()
                numverts = len(flatverts) / 2
                self.batch.add(
                    numverts,
                    primitive.primtype,
                    None,
                    ('v2f/static', flatverts),
                    ('c3B/static', primitive.color * numverts)
                )
        return self.batch

from math import cos, pi, sin
from random import uniform

class Creature(object):
    "Stores the world-coordinates and shape of a rendered monster"

    def __init__(self, shape, position=None, angle=None):
        self.shape = shape
        if position is None:
            position = (0, 0)
        self.x, self.y = position
        if angle is None:
            angle = uniform(-pi, +pi)
        self.angle = angle
        self.da = 0
        self.velocity = 0

    def update(self, dt):
        self.angle += self.da
        self.x -= self.velocity * cos(self.angle)
        self.y -= self.velocity * sin(self.angle)

class Color(object):
    orange = (255, 127, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)
    yellow = (255, 255, 0)
    red = (200, 0, 0)
    blue = (127, 127, 255)
    pink = (255, 187, 187)

eye_white = [
    (-1, -2.5),
    (-2, -1.5),
    (+1, -2.5),
    (-2, +1.5),
    (+2, -1.5),
    (-1, +2.5),
    (+2, +1.5),
    (+1, +2.5),
]
eye_pupil = [
    (-1, -1),
    (-1, +1),
    (+1, -1),
    (+1, +1),
]
eye_left = Shape([
    Primitive(eye_white, Color.white).offset(+2, +1.5),
    Primitive(eye_pupil, Color.black).offset(+1, +2)
])
eye_right = Shape([
    Primitive(eye_white, Color.white).offset(-4, +1.5),
    Primitive(eye_pupil, Color.black).offset(-5, +2)
])

ghost_body1 = [
    (-7, -7),   # 0
    (-7.0, 0.0),# 1
    (-5, -5),   # 22
    (-6.7, 2.0),# 2
    (-3, -7),   # 21
    (-5.9, 3.8),# 3
    (-1, -7),   # 20
    (-4.6, 5.3),# 4
    (-1, -5),   # 19
    (-2.9, 6.4),# 5
    (1, -5),    # 18
    (-1.0, 6.9),# 6
    (3, -7),    # 16
    (1.0, 6.9), # 7
    (5, -5),    # 15
    (2.9, 6.4), # 8
    (7, -7),    # 14
    (4.6, 5.3), # 9
    (7.0, 0.0), # 13
    (4.6, 5.3), # 10
    (6.7, 2.0), # 12
    (5.9, 3.8), # 11
]
ghost_body2 = [
    (3, -7),    # 16
    (1, -7),    # 17
    (1, -5),    # 18
]

orange_ghost = Shape([
    Primitive(ghost_body2, Color.orange),
    Primitive(ghost_body1, Color.orange),
    eye_left,
    eye_right,
])
orange_ghost.get_batch()
red_ghost = Shape([
    Primitive(ghost_body2, Color.red),
    Primitive(ghost_body1, Color.red),
    eye_left,
    eye_right,
])
red_ghost.get_batch()
blue_ghost = Shape([
    Primitive(ghost_body2, Color.blue),
    Primitive(ghost_body1, Color.blue),
    eye_left,
    eye_right,
])
blue_ghost.get_batch()
pink_ghost = Shape([
    Primitive(ghost_body2, Color.pink),
    Primitive(ghost_body1, Color.pink),
    eye_left,
    eye_right,
])
pink_ghost.get_batch()

pac_body1 = [
    (-6.7, 2.0),  # 1
    (0, 0),       # 0
    (-5.9, 3.8),  # 2
    (7.0, 0.0),   # 11
    (-4.6, 5.3),  # 3
    (6.7, 2.0),   # 10
    (-2.9, 6.4),  # 4
    (5.9, 3.8),   # 9
    (-1.0, 6.9),  # 5
    (4.6, 5.3),   # 8
    (1.0, 6.9),   # 6
    (2.9, 6.4),   # 7
]
pac_body2 = [
    (-6.7, -2.0), # 21
    (0, 0),       # 0
    (-5.9, -3.8), # 20
    (7.0, 0.0),   # 11
    (-4.6, -5.3), # 19
    (6.7, -2.0),  # 12
    (-2.9, -6.4), # 18
    (5.9, -3.8),  # 13
    (-1.0, -6.9), # 17
    (4.6, -5.3),  # 14
    (1.0, -6.9),  # 16
    (2.9, -6.4),  # 15
]

pacman = Shape([
    Primitive(pac_body1, Color.yellow),
    Primitive(pac_body2, Color.yellow),
    Primitive(eye_pupil, Color.black).offset(0, +4),
])
pink_ghost.get_batch()

class Spin:

    def __init__(self):
        self.MAX_SPIN_SPEED = 50
        self.degrees = 0
        self.start()
        self.time_elapsed = 0


    def stop(self):
        self.velocity = 0
        self.acceleration = 0

    def start(self):
        self.velocity = 7
        self.acceleration = 0.07

    def update(self):
        self.time_elapsed += pyglet.clock.tick()
        t = self.time_elapsed % 0.05 # 600 Cycle
        self.degrees = t / 0.05 * 360
        # print "Time: %f, T: %f, DEGREE %f"%(self.time_elapsed, t, self.degrees)

        # if self.velocity >= self.MAX_SPIN_SPEED:
        #     self.velocity = self.MAX_SPIN_SPEED
        # self.velocity = self.velocity + self.acceleration
        # self.degrees = self.degrees + self.velocity


    def draw(self, x, y):
        self.update()

        glPushMatrix()
        glTranslatef(x, y, 0)
        glColor4f(100, 100, 100, 100)
        glRotatef(self.degrees, 0,0,1)
        glTranslatef(-15, -15, 0)
        ellipse_outline(0,0,10,10)
        line(8,8,15,15)
        line(15,15,22,22)
        ellipse_outline(20,20,30,30)
        glPopMatrix()


from random import randint, uniform


def make_army(size, menagerie):
    army = []
    for col in range(size):
        for row in range(size):
            creature_type = menagerie[randint(0, len(menagerie)-1)]
            x = (col+0.5)*16 - size * 8
            y = (row+0.5)*16 - size * 8
            creature = Creature(creature_type, (x, y))
            creature.da = uniform(-0.1, +0.1)
            creature.velocity = uniform(0, +0.5)
            army.append(creature)
    return army

class SpinShape:
    def make_spin(self, size, spin_shape):
        spins = []
        for col in range(size):
            for row in range(size):
                s = spin_shape
                x = (col+0.5)*70- size * 8
                y = (row+0.5)*70 - size * 8
                creature = Creature(s, (x, y))
                creature.da = uniform(-0.1, +0.1)
                creature.velocity = uniform(0, +1.5)
                spins.append(creature)
        return spins

    def make_cubes(self, size, cube_shape):
        spins = []
        s = cube_shape
        creature = Creature(s, (300, 300))
        creature.da = 0
        creature.velocity = 0
        spins.append(creature)
        return spins

    def __init__(self):
        # self.creatures = make_army(12, [blue_ghost, orange_ghost, pacman,
        # pink_ghost, red_ghost])
        self.init_spin()
        self.init_cube()

    def init_spin(self):
        self.spins = []
        spin_bar = [
            10,10,
            22,22,
            23,23,
        ]

        ellipse_white_l = _concat(_iter_ellipse(0, 0, 10, 10))

        self.spin = Shape([
            Primitive(zip(ellipse_white_l[::2], ellipse_white_l[1::2]), Color.white, GL_LINE_LOOP),
            Primitive(zip(spin_bar[::2], spin_bar[1::2]), Color.white, GL_LINE_LOOP),
            Primitive(zip(ellipse_white_l[::2], ellipse_white_l[1::2]), Color.white, GL_TRIANGLE_FAN).offset(+20, +20),
            Primitive([(22,22),(10,10)], Color.white, GL_LINE_LOOP),
        ])
        self.spins = self.make_spin(4, self.spin)

    def make_cube(self, angle):
        rad = angle * 3.14 /180.0
        return project_3d_mesh_to_2d_lines(Cube(50).translate((100,100,-0)).rotate_at_y(rad,(0,0,1)))

    def init_cube(self):
        self.cube = Shape(
            [ Primitive(x, Color.orange, GL_TRIANGLE_STRIP) for x in self.make_cube(0)]
        )
        self.spins = self.make_spin(4, self.cube)
        return self.spins

    def update_cube(self, dt):
        self.cube = Shape(
            [ Primitive(x, Color.orange, GL_LINE_LOOP) for x in self.make_cube(dt)]
        )
        self.spins = self.make_cubes(4, self.cube)
        
    def draw(self):
        rad2deg = 180 / 3.14
        global x
        for i, creature in enumerate(self.spins):
            creature.update(1) # 1 is dummy
            # x = (x+1) % 360
            self.update_cube(x)
            glPushMatrix()
            # print "(%d, %d)" % (creature.x, creature.y)
            batch = creature.shape.get_batch()
            batch.draw()
            glPopMatrix()


x=0
