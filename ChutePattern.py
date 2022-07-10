""" ChuteMaker
Copyright (C) 2022 Thomas Schmid

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""

import cairo
import shapely.geometry as spg
from shapely.geometry.base import JOIN_STYLE
import numpy as np
import enum
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

class MitreType(enum.Enum):
    none=0
    bevel=1
    miter=2
    round=3


class ChutePattern:
    def __init__(self, grid, seam_allowance=(10,10,10,10)):
        self.grid = grid
        self.seam_allowance=seam_allowance
        self.joint_style = MitreType.none

    def set_joint_style(self, joint_style):
        self.joint_style = joint_style

    def set_grid(self, grid):
        self.grid = grid

    def description(self):
        pass

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

    def add_seamallowance_bevel(self, lines, seam_allowance):
        coords = list()

        for i,l in enumerate(lines):
            if l.length <= 0.001:
                print(l)
                continue
            if seam_allowance[i] > 0:
                ol = l.parallel_offset(seam_allowance[i], "right")
                coord = list(ol.coords[::-1])
            else:
                coord = list(l.coords)
            coords.extend(coord)

        return spg.Polygon(coords)

    def print_info(self, ctx):
        font_size = 3
        ctx.set_font_size(3)
        ctx.set_source_rgba(0, 0, 0, 0.5)
        lines = list()
        for k, v in self.description().items():
            lines.append(f"{k}: {v}")

        y_pos = 10
        for l in lines:
            y_pos += font_size
            ctx.move_to(10, y_pos)
            ctx.show_text(l)

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

        if self.joint_style == MitreType.none:
            if self.seam_allowance[0] > 0:
                polygon = self.add_seamallowance(polygon, line_right, self.seam_allowance[0])
            if self.seam_allowance[1] > 0:
                polygon = self.add_seamallowance(polygon, line_top, self.seam_allowance[1])
            if self.seam_allowance[2] > 0:
                polygon = self.add_seamallowance(polygon, line_left, self.seam_allowance[2])
            if self.seam_allowance[3] > 0:
                polygon = self.add_seamallowance(polygon, line_bottom, self.seam_allowance[3])
        elif len(set(self.seam_allowance)) == 1:
            if self.joint_style == MitreType.miter:
                jt = JOIN_STYLE.mitre
            elif self.joint_style == MitreType.bevel:
                jt = JOIN_STYLE.bevel
            elif self.joint_style == MitreType.round:
                jt = JOIN_STYLE.round
            polygon = polygon.buffer(self.seam_allowance[0], join_style=jt, mitre_limit=2)
        elif self.joint_style == MitreType.bevel:
            polygon = self.add_seamallowance_bevel([line_right, line_top, line_left, line_bottom], self.seam_allowance)
        elif self.joint_style == MitreType.round:
            print("ERROR: joint style \"round\" not supported for non uniform seam allowance. Please use bevel or none")
        elif self.joint_style == MitreType.miter:
            print("ERROR: joint style \"miter\" not supported for non uniform seam allowance. Please use bevel or none")

        u,l = polygon.exterior.xy

        u = np.array(u)
        l = np.array(l)

        margins = (10, 10, 10, 10)
        l = l * -1
        li = li * -1

        pattern_extend = (np.min(u), np.min(l), np.max(u), np.max(l))
        pattern_width = pattern_extend[2] - pattern_extend[0]
        pattern_height = pattern_extend[3] - pattern_extend[1]

        document_width = pattern_width + margins[0] + margins[1]
        document_height = pattern_height + margins[2] + margins[3]

        surface = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, cairo.Rectangle(0, 0, mm_to_pt(document_width), mm_to_pt(document_height)))
        ctx = cairo.Context(surface)
        ctx.save()
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.push_group()
        ctx.scale(mm_to_pt(1), mm_to_pt(1))
        ctx.save()

        if self.grid:
            draw_grid(ctx, (0,0), 10, 1, document_height, document_width)

        #draw seam allowance
        ctx.translate(-pattern_extend[0] + (document_width/2 - pattern_width/2),
                      -pattern_extend[1] + (document_height/2 - pattern_height/2))
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
        self.print_info(ctx)
        pattern = ctx.pop_group()
        return (pattern, (document_width, document_height))
