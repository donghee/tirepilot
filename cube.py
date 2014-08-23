#!/usr/bin/env python

import copy
import pyglet
import time
import math
from pyglet.gl import *
from pyglet.window import key

FOV_FACTOR = 1.0 / math.tan(90 / 360.0 * 2 * math.pi / 2)

class Mesh(object):
    @property
    def vertices(self):
        return self._vertices
    @property
    def edges(self):
        return [(self._vertices[a], self._vertices[b]) for a,b in self._edges_indices]
    #return map (lambda e: (self._vertices[e[0]], self._vertices[e[1]]), self._edges_indices)
    #def faces(self):

    def translate(self, vector):
        res = copy.deepcopy(self)
        res._vertices = [(v[0]+vector[0], v[1]+vector[1], v[2]+vector[2]) for v in res._vertices]
        return res
    def rotate(self, matrix):
        m = matrix
        res = copy.deepcopy(self)
        res._vertices = [(m[0][0]*x  + m[0][1]*y + m[0][2]*z,
                          m[1][0]*x  + m[1][1]*y + m[1][2]*z,
                          m[2][0]*x  + m[2][1]*y + m[2][2]*z) for x,y,z in res._vertices]
        return res
    def rotate_at(self, matrix, vector):
        return self.translate((-vector[0], -vector[1], -vector[2])).rotate(matrix).translate(vector)


"""
Initially, (0,0,0) is the center of the cube. Edges
are parallel to the axes.
"""
class Cube(Mesh):
    def __init__(self, size):
        s = float(size) / 2
        self._vertices = [  ( s, s, s), #0
                            ( s, s,-s), #1
                            ( s,-s, s), #2
                            ( s,-s,-s), #3
                            (-s, s, s), #4
                            (-s, s,-s), #5
                            (-s,-s, s), #6
                            (-s,-s,-s)] #7

        self._edges_indices = [ (0,1), (0,2), (0,4), (1,3), 
                                (1,5), (2,3), (2,6), (3,7), 
                                (4,5), (4,6), (5,7), (6,7)]


    def rotate_at_y(self, angle,vector ):
        sin = math.sin(angle)
        cos = math.cos(angle)
        matrix = [[cos,  0, sin],
                [0,    1, 0  ],
                [-sin, 0, cos]]

        return self.rotate_at(matrix, vector)


def draw_line(canvas, line):
    ((start_x,start_y), (end_x,end_y)) = line


def project_3d_to_2d(cam_z, point3d):
	a = float(cam_z) / (cam_z - point3d[2])
	x = point3d[0] * a
	y = point3d[1] * a
	return (x,y)

def project_3d_mesh_to_2d_lines(mesh):
	cam_z = 640 / 1.0 * FOV_FACTOR
	result = []
	for e in mesh.edges:
		if e[0][2] <= 0 and e[1][2] <= 0:
			result.append((project_3d_to_2d(cam_z, e[0]), project_3d_to_2d(cam_z, e[1])))
		elif e[0][2] > 0 and e[1][2] > 0:
			pass
		else:
			r = float(e[0][2]) / (e[0][2] - e[1][2])
			x = e[0][0] + r * (e[1][0] - e[0][0])
			y = e[0][1] + r * (e[1][1] - e[0][1])
			if e[0][2] > 0:
				result.append(((x,y), project_3d_to_2d(cam_z, e[1])))
			else:
				result.append((project_3d_to_2d(cam_z, e[0]), (x,y)))
	return result

