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
import util
import math

PAPER_SIZES = {
    "4A0": (1682, 2378),
    "2A0": (1189, 1682),
    "A0": (841, 1189),
    "A1": (594, 841),
    "A2": (420, 594),
    "A3": (297, 420),
    "A4": (210, 297),
    "A5": (148, 210),
    "A6": (105, 148),
    "A7": (74, 105),
    "A8": (52, 74),
    "A9": (37, 52),
    "A10": (26, 37),
    "Letter": (216, 279),
    "Legal": (216, 356),
    "Tabloid": (279, 432),
    "Ledger": (432, 279),
    "Junior Legal": (127, 203),
    "Half Letter": (140, 216),
    "Government Letter": (203, 267),
    "Government Legal": (216, 330),
    "ANSI A": (216, 279),
    "ANSI B": (279, 432),
    "ANSI C": (432, 559),
    "ANSI D": (559, 864),
    "ANSI E": (864, 1118),
    "ARCH A": (229, 305),
    "ARCH B": (305, 457),
    "ARCH C": (457, 610),
    "ARCH D": (610, 914),
    "ARCH E": (914, 1219),
    "ARCH E1": (762, 1067),
    "ARCH E2": (660, 965),
    "ARCH E3": (686, 991)
}

class CairoTiler:
    def __init__(self, pattern, size, paper_size = (210, 297), margins = (10,10,10,10), overlap=10, overview=True):
        self.pattern = pattern
        self.size = size
        self.paper_size = paper_size
        self.overlap = overlap
        self.margins = margins
        self.overview = overview

    def draw_alignment_mark(self, ctx, pos, rotation=0, flipx=False, flipy=False):
        ctx.save()
        ctx.scale(util.mm_to_pt(1), util.mm_to_pt(1))
        ctx.translate(*pos)
        if flipy:
            ctx.scale(1, -1)
        if flipx:
            ctx.scale(-1, 1)
        ctx.rotate(rotation)
        ctx.set_source_rgb(0,0,0)
        ctx.move_to(-5,0)
        ctx.line_to(0, 0)
        ctx.line_to(0, self.overlap)
        ctx.line_to(-5, self.overlap)
        ctx.move_to(0, self.overlap/2)
        ctx.line_to(-2, self.overlap/2)
        ctx.set_line_width(0.3)
        ctx.stroke()
        ctx.restore()

    def draw_alignment_marks(self, ctx):
        ctx.save()
        ctx.scale(util.mm_to_pt(1), util.mm_to_pt(1))
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
        surface = cairo.PDFSurface(output, util.mm_to_pt(self.paper_size[0]), util.mm_to_pt(self.paper_size[1]))
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
                mat.translate(util.mm_to_pt(xoff-self.margins[2]), util.mm_to_pt(yoff-self.margins[1]))
                #ctx.translate(util.mm_to_pt(-xoff), util.mm_to_pt(-yoff))s
                ctx.rectangle(util.mm_to_pt(self.margins[2]),
                              util.mm_to_pt(self.margins[1]),
                              util.mm_to_pt((self.paper_size[0] - self.margins[0] - self.margins[2])),
                              util.mm_to_pt((self.paper_size[1] - self.margins[1] - self.margins[3])))
                ctx.clip()
                self.pattern.set_matrix(mat)
                ctx.set_source(self.pattern)
                ctx.paint()
                ctx.reset_clip()

                ul = (self.margins[2], self.margins[1])
                ur = (self.paper_size[0] - self.margins[0], ul[1])
                ll = (ul[0], self.paper_size[1] - self.margins[2])
                lr = (ur[0], ll[1])

                if j > 0:
                    #Upper horizontal alignment marks
                    self.draw_alignment_mark(ctx, (self.margins[2], self.margins[1]))
                    self.draw_alignment_mark(ctx, (self.paper_size[0] - self.margins[0], self.margins[1]), flipx=True)

                if j < (m-1):
                    #Lower horizontal alignment marks
                    self.draw_alignment_mark(ctx, ll, flipy=True)
                    self.draw_alignment_mark(ctx, lr, flipx=True, flipy=True)

                if i > 0:
                    #Left vertical alignment marks
                    self.draw_alignment_mark(ctx, ul, rotation=math.pi/2, flipx=True)
                    self.draw_alignment_mark(ctx, ll, rotation=math.pi/2, flipy=True, flipx=True)

                if i < (n-1):
                    #Right vertical alignment marks
                    self.draw_alignment_mark(ctx, ur, rotation=math.pi/2)
                    self.draw_alignment_mark(ctx, lr, rotation=math.pi/2, flipy=True)
                #ctx.translate(util.mm_to_pt(xoff), util.mm_to_pt(yoff))
                ctx.show_page()
