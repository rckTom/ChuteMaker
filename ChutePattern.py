import cairo
import shapely.geometry as spg
import shapely.ops as spo
import numpy as np
from util import mm_to_pt

def draw_grid(ctx, offset, major_tick, minor_tick, height, width):
    x_minorticks = np.arange(0, width, minor_tick)
    x_majorticks = np.arange(0, width, major_tick)
    y_minorticks = np.arange(0, height, minor_tick)
    y_majorticks = np.arange(0, height, major_tick)

    ctx.save()
    ctx.push_group()
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

class ChutePattern:
    def __init__(self, grid, seam_allowance=(10,10,10,10)):
        self.grid = grid
        self.seam_allowance=seam_allowance

    def set_grid(self, grid):
        self.grid = grid

    def _get_pattern_path(self):
        return (np.array([]), np.array([]))

    def add_seamallowance(self, polygon, line, seam_allowance):
        if line.length < 0.01:
            return polygon

        offset_line = line.parallel_offset(seam_allowance, "right")
        coord = list(line.coords)
        coord1 = list(offset_line.coords)
        coord.extend(coord1)
        seam = spg.Polygon(coord)
        return polygon.union(seam)

    def get_pattern(self):
        pattern_lines = self._get_pattern_path()
        line_right = spg.LineString(pattern_lines["right"])
        line_top = spg.LineString(pattern_lines["top"])
        line_left = spg.LineString(pattern_lines["left"])
        line_bottom = spg.LineString(pattern_lines["bottom"])

        coords = list()
        coords.extend(line_right.coords)
        coords.extend(line_top.coords)
        coords.extend(line_left.coords)
        coords.extend(line_bottom.coords)
 
        polygon = spg.Polygon(coords)
        ui, li = polygon.exterior.xy

        ui = np.array(ui)
        li = np.array(li)

        if self.seam_allowance[0] > 0:
            polygon = self.add_seamallowance(polygon, line_right, self.seam_allowance[0])

        if self.seam_allowance[1] > 0:
            polygon = self.add_seamallowance(polygon, line_top, self.seam_allowance[1])

        if self.seam_allowance[2] > 0:
            polygon = self.add_seamallowance(polygon, line_left, self.seam_allowance[2])

        if self.seam_allowance[3] > 0:
            polygon = self.add_seamallowance(polygon, line_bottom, self.seam_allowance[3])

        u,l = polygon.exterior.xy

        u = np.array(u)
        l = np.array(l)
        
        margins = (10, 10, 10, 10)
        pattern_extend = (np.min(u), np.min(l), np.max(u), np.max(l))
        pattern_width = pattern_extend[2] - pattern_extend[0]
        pattern_height = pattern_extend[3] - pattern_extend[1]

        l = l * -1 + pattern_height
        li = li * -1 + pattern_height

        document_width = pattern_width + margins[0] + margins[1]
        document_height = pattern_height + margins[2] + margins[3]

        surface = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, cairo.Rectangle(0, 0, mm_to_pt(document_width), mm_to_pt(document_height)))
        ctx = cairo.Context(surface)
        ctx.save()
        ctx.push_group()
        ctx.scale(mm_to_pt(1), mm_to_pt(1))
        ctx.save()

        if self.grid:
            draw_grid(ctx, (0,0), 10, 1, document_height, document_width)

        #draw seam allowance
        ctx.translate(document_width/2, 0)
        ctx.move_to(u[0], l[0])
        for x,y in zip(u, l):
            ctx.line_to(x, y)
        ctx.close_path()
        ctx.set_source_rgb(.0, .0, .0)
        ctx.set_line_width(0.3)
        ctx.stroke()

        #draw pattern
        ctx.move_to(ui[0], li[0])
        for x,y in zip(ui, li):
            ctx.line_to(x, y)
        ctx.close_path()
        ctx.set_source_rgb(1, .0, .0)
        ctx.set_line_width(0.3)
        ctx.stroke()
        ctx.restore()
        pattern = ctx.pop_group()
        return (pattern, (document_width, document_height))
