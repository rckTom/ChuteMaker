import argparse
import math

import cairo
import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.polynomial import poly
from scipy import integrate

import shapely.geometry as spg
import shapely.ops as spo
import matplotlib.pyplot as plt


def mm_to_pt(mm):
    return mm * 72/25.4

def circle_perimeter(r):
    return 2*math.pi*r

def circle(center, r):
    point = spg.Point(*center)
    circle = point.buffer(r)
    return circle

def ellipse(center, a, b):
    circ = circle(center, a)
    return circ.scale(circ, yfact = b/a, origin=center)

def draw_grid(ctx, offset, major_tick, minor_tick, height, width):
    x_minorticks = np.arange(0, width, minor_tick)
    x_majorticks = np.arange(0, width, major_tick)
    y_minorticks = np.arange(0, height, minor_tick)
    y_majorticks = np.arange(0, height, major_tick)

    ctx.save()
    ctx.push_group()
    ctx.scale(mm_to_pt(1), mm_to_pt(1))
    ctx.set_line_width(0.03)
    ctx.set_source_rgb(0.9,0.9,0.9)
    for x in x_minorticks:
        x1 = x + offset[0]
        y1 = 0 + offset[1]
        x2 = x1
        y2 = y1 + height
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)

    ctx.set_line_width(0.03)
    ctx.set_source_rgb(0.9, 0.9, 0.9)
    for y in y_minorticks:
        x1 = 0 + offset[0]
        y1 = y + offset[1]
        x2 = x1 + width
        y2 = y1

        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)

    ctx.stroke()

    ctx.set_line_width(0.1)
    ctx.set_source_rgb(0.9,0.9,0.9)
    for x in x_majorticks:
        x1 = x + offset[0]
        y1 = 0 + offset[1]
        x2 = x1
        y2 = y1 + height
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)

    ctx.set_line_width(0.1)
    ctx.set_source_rgb(0.9, 0.9, 0.9)
    for y in y_majorticks:
        x1 = 0 + offset[0]
        y1 = y + offset[1]
        x2 = x1 + width
        y2 = y1
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
  
    ctx.stroke()
    ctx.pop_group_to_source()
    ctx.paint()
    
    ctx.restore()

class CairoTiler:
    def __init__(self, pattern, size, paper_size = (210, 297), margins = (5,5,5,5), overlap=10):
        self.pattern = pattern
        self.size = size
        self.paper_size = paper_size
        self.overlap = overlap
        self.margins = margins

    def draw_alignment_mark(self, ctx, pos, rotation):
        ctx.save()
        ctx.scale(mm_to_pt(1), mm_to_pt(1))
        ctx.set_source_rgb(0,0,0)
        ctx.new_path()
        ctx.move_to(pos)
        ctx.restore()

    def draw_alignment_marks(self, ctx):
        ctx.save()
        ctx.scale(mm_to_pt(1), mm_to_pt(1))
        ctx.set_source_rgb(0,0,0)
        ctx.new_path()
        ctx.move_to(0, self.overlap)
        ctx.line_to(self.overlap, self.overlap)
        ctx.line_to(self.overlap, 0)

        ctx.move_to(self.paper_size[0], self.overlap)
        ctx.move_to(self.paper_size[0]-self.overlap, self.overlap)
        ctx.move_to(self.paper_size[0]-self.overlap, 0)
        ctx.set_line_width(0.5)
        ctx.stroke()
        ctx.restore()

    def tile(self, output):
        surface = cairo.PDFSurface(output, mm_to_pt(self.paper_size[0]), mm_to_pt(self.paper_size[1]))
        ctx = cairo.Context(surface)

        n = math.ceil(self.size[0] / (self.paper_size[0]-self.overlap-self.margins[0]-self.margins[2]))
        m = math.ceil(self.size[1] / (self.paper_size[1]-self.overlap-self.margins[1]-self.margins[3]))

        for i in range(0, n):
            for j in range(0, m):
                ctx.reset_clip()
                ctx.identity_matrix()
                xoff = i * ((self.paper_size[0] - self.margins[0] - self.margins[2])- self.overlap)
                yoff = j * ((self.paper_size[1] - self.margins[1] - self.margins[3])- self.overlap)
                mat = cairo.Matrix()
                mat.translate(mm_to_pt(xoff-self.margins[2]), mm_to_pt(yoff-self.margins[1]))
                #ctx.translate(mm_to_pt(-xoff), mm_to_pt(-yoff))
                ctx.rectangle(mm_to_pt(self.margins[2]),
                              mm_to_pt(self.margins[1]),
                              mm_to_pt((self.paper_size[0] - self.margins[0] - self.margins[2])),
                              mm_to_pt((self.paper_size[1] - self.margins[1] - self.margins[3])))
                ctx.clip()
                self.pattern.set_matrix(mat)
                ctx.set_source(self.pattern)
                ctx.paint()
                #ctx.translate(mm_to_pt(xoff), mm_to_pt(yoff))
                ctx.show_page()

class ChutePattern:
    def __init__(self, grid):
        self.grid = grid

    def set_grid(self, grid):
        self.grid = grid

    def _get_pattern_path(self):
        return (np.array([]), np.array([]))

    def get_pattern(self):
        pattern_lines = self._get_pattern_path()
        line_right = spg.LineString(pattern_lines["right"])
        line_top = spg.LineString(pattern_lines["top"])
        line_left = spg.LineString(pattern_lines["left"])
        line_bottom = spg.LineString(pattern_lines["bottom"])

        line_right_offset = line_right.parallel_offset(10, "right")
        line_top_offset = line_top.parallel_offset(10, "right")
        line_left_offset = line_left.parallel_offset(10, "right")
        line_bottom_offset = line_bottom.parallel_offset(10, "right")

        coords = list()
        coords.extend(line_right.coords)
        coords.extend(line_top.coords)
        coords.extend(line_left.coords)
        coords.extend(line_bottom.coords)
 
        polygon = spg.Polygon(coords)
        ui, li = polygon.exterior.xy

        ui = np.array(ui)
        li = np.array(li)

        coord = list(line_right.coords)
        coord1 = list(line_right_offset.coords)
        coord.extend(coord1)
        right_offset = spg.Polygon(coord)

        coord = list(line_top.coords)
        coord1 = list(line_top_offset.coords)
        coord.extend(coord1)
        top_offset = spg.Polygon(coord)

        coord = list(line_left.coords)
        coord1 = list(line_left_offset.coords)
        coord.extend(coord1)
        left_offset = spg.Polygon(coord)

        coord = list(line_bottom.coords)
        coord1 = list(line_bottom_offset.coords)
        coord.extend(coord1)
        bottom_offset = spg.Polygon(coord)

        polygon = polygon.union(right_offset)
        polygon = polygon.union(top_offset)
        polygon = polygon.union(left_offset)
        polygon = polygon.union(bottom_offset)

        u,l = polygon.exterior.xy

        u = np.array(u)
        l = np.array(l)
        
        margins = (10, 10, 10, 10)
        pattern_extend = (np.min(u), np.min(l), np.max(u), np.max(l))
        print(pattern_extend)
        pattern_width = pattern_extend[2] - pattern_extend[0]
        pattern_height = pattern_extend[3] - pattern_extend[1]

        print(pattern_width, pattern_height)
        l = l * -1 + pattern_height
        li = li * -1 + pattern_height
        pattern_mid = (pattern_extend[0] + pattern_width/2, pattern_extend[1] + pattern_height/2)

        document_width = pattern_width + margins[0] + margins[1]
        document_height = pattern_height + margins[2] + margins[3]

        surface = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, cairo.Rectangle(0, 0, mm_to_pt(document_width), mm_to_pt(document_height)))
        ctx = cairo.Context(surface)
        ctx.save()
        ctx.push_group()
        ctx.save()
        if self.grid:
            draw_grid(ctx, (0,0), 10, 1, mm_to_pt(document_height), mm_to_pt(document_width))

        #draw outer
        ctx.translate(mm_to_pt(document_width/2), 0)
        ctx.move_to(mm_to_pt(u[0]), mm_to_pt(l[0]))
        for x,y in zip(u, l):
            ctx.line_to(mm_to_pt(x),mm_to_pt(y))
        ctx.close_path()
        ctx.set_source_rgb(.0, .0, .0)
        ctx.set_line_width(0.3)
        ctx.stroke()

        #draw inner
        ctx.move_to(mm_to_pt(ui[0]), mm_to_pt(li[0]))
        for x,y in zip(ui, li):
            ctx.line_to(mm_to_pt(x),mm_to_pt(y))
        ctx.close_path()
        ctx.set_source_rgb(1, .0, .0)
        ctx.set_line_width(0.3)
        ctx.stroke()
        ctx.restore()

        pattern = ctx.pop_group()
        return (pattern, (document_width, document_height))

class EllipticChutePattern(ChutePattern):
    def __init__(self, diameter, num_panels, e, tangent_lines=True, line_length = None, spill_hole_diameter = None, grid=True):
        self.diameter = diameter
        self.radius = diameter/2
        self.num_panels = num_panels
        self._a = self.radius
        self._b = self.radius * e
        self._e = e
        self.spill_hole = spill_hole_diameter

        self.tangent_lines = tangent_lines

        if self.tangent_lines and not line_length:
            self.line_length = 2*self.diameter
        else:
            self.line_length = line_length

        super().__init__(grid)

    def _elliptic_x(self, t):
        return self.radius * math.cos(t)

    def _elliptic_y(self, t):
        return self.radius * self.e * math.sin(t)

    def _tangential_line_point(self):
        l2 = self.line_length**2
        r2 = self.radius**2
        e2 = self._e**2

        x = math.sqrt(2)/2 * math.sqrt((-l2-r2+math.sqrt(4*e2*l2*r2+l2**2-2*l2*r2+r2**2))/(e2-1))
        t = math.acos(x/self._a)

        return t

    def _elliptic_integral(self, t):
        return math.sqrt(self._a**2 * math.sin(t)**2 + self._b**2 * math.cos(t)**2)

    def _get_pattern_path(self):
        tmin = -self._tangential_line_point()

        if self.spill_hole:
            tmax = math.acos(self.spill_hole/(2*self._a))
        else:
            tmax = math.pi/2
        n = 100

        ts = np.linspace(tmin, tmax, n)
        x = [self._elliptic_x(t) for t in ts]
        y = [self._elliptic_integral(t) for t in ts]

        u = np.array([math.pi*xe for xe in x]) / self.num_panels
        l = integrate.cumtrapz(y = y, x = ts, initial = 0)

        right_x = u
        right_y = l

        left_x = [-e for e in u[::-1]]
        left_y = [e for e in l[::-1]]

        top_x = [right_x[-1], left_x[0]]
        top_y = [right_y[-1], left_y[0]]

        bottom_x = [left_x[-1], right_x[0]]
        bottom_y = [left_y[-1], right_y[0]]

        return {"right": zip(right_x, right_y),
                "top": zip(top_x, top_y),
                "left" : zip(left_x, left_y),
                "bottom": zip(bottom_x, bottom_y)}

        # u = np.append(u, [-e for e in u[::-1]])
        # l = np.append(l, [e for e in l[::-1]])

        # return (u,l)

class ToroidalChutePattern(ChutePattern):
    def __init__(self, diameter, radius, num_panels, e, tangent_lines=True, line_length = None, spill_hole_diameter = 0, grid=True):
        self.line_length = line_length
        self.r = radius
        self.rt = diameter/2-self.r
        self.rs = spill_hole_diameter/2
        self.num_panels = num_panels
        super().__init__(grid)

    def _t(self, x):
        return math.acos((x-self.rt)/self.r)

    def _x(self, t):
        return self.rt + math.cos(t) * self.r

    def _y(self, t):
        return self.rt + math.sin(t) * self.r

    def _tangential_line_point(self):
        l = self.line_length
        r = self.r
        rt = self.rt
        x = l*(l*rt + r*math.sqrt(l**2 + r**2 - rt**2))/(l**2 + r**2)
        print(x)
        return self._t(x)

    def _get_pattern_path(self):
        minx = self.rt - self.r

        if (minx > self.rs):
            self.rs = minx
            print("WARNING: spill hole to small. Extend it to minimal possible size")
        elif (self.rs >= self.rt):
            print("WARNING: spill hole diameter to large. Scaling it down")
            self.rs = self.rt

        tmin = -self._tangential_line_point()
        tmax = self._t(self.rs)
        n = 100

        ts = np.linspace(tmin, tmax, n)
        x = [self._x(t) for t in ts]
        l = [(t-tmin) * self.r for t in ts]

        u = np.array([math.pi*xe for xe in x]) / self.num_panels

        right_x = u
        right_y = l

        left_x = [-e for e in u[::-1]]
        left_y = [e for e in l[::-1]]

        top_x = [right_x[-1], left_x[0]]
        top_y = [right_y[-1], left_y[0]]

        bottom_x = [left_x[-1], right_x[0]]
        bottom_y = [left_y[-1], right_y[0]]

        return {"right": zip(right_x, right_y),
                "top": zip(top_x, top_y),
                "left" : zip(left_x, left_y),
                "bottom": zip(bottom_x, bottom_y)}

def main(args):
    ep = EllipticChutePattern(500, 12, 0.7, line_length=1000, spill_hole_diameter=100)
    #ep = ToroidalChutePattern(1000, 200, 10, 0.7, line_length=1000, spill_hole_diameter=700)
    pattern, size = ep.get_pattern()

    surface = cairo.SVGSurface(args.output, mm_to_pt(size[0]), mm_to_pt(size[1]))
    ctx = cairo.Context(surface)
    #ctx.scale(72/25.4, 72/25.4)
    ctx.push_group()
    ctx.set_source(pattern)
    ctx.paint()
    pattern2 = ctx.pop_group()

    ctx.set_source(pattern2)
    ctx.paint()

    tiler = CairoTiler(pattern2, size)
    tiler.tile("tiled.pdf")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output")

    args = parser.parse_args()
    main(args)
