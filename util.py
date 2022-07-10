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

import math

def mm_to_pt(mm):
    return mm * 72/25.4

def arrow(ctx, start, end, head_size=10, arrow_start = False, arrow_end = True):
    angle = math.atan2(end[1] - start[1], end[0] - start[0])

    ctx.move_to(start)
    if arrow_start:
        ctx.rel_line_to(head_size * math.cos(-angle - math.pi + 30*math.pi/180), head_size * math.sin(-angle - math.pi + 30*math.pi/180))
        ctx.move_to(start)
        ctx.rel_line_to(head_size * math.cos(-angle - math.pi - 30*math.pi/180), head_size * math.sin(-angle - math.pi - 30*math.pi/180))
        ctx.move_to(start)  
    
    ctx.line_to(end)
    if arrow_end:
        ctx.rel_line_to(head_size * math.cos(angle - math.pi + 30*math.pi/180), head_size * math.sin(angle - math.pi + 30*math.pi/180))
        ctx.move_to(end)
        ctx.rel_line_to(head_size * math.cos(angle - math.pi - 30*math.pi/180), head_size * math.sin(angle - math.pi - 30*math.pi/180))
