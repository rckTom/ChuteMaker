import argparse
import math

import cairo
import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.polynomial import poly

import util
from ToroidalChutePattern import ToroidalChutePattern
from EllipticalChutePattern import EllipticChutePattern
from CairoTiler import CairoTiler, PAPER_SIZES

def main(chute, args):
    pattern, size = chute.get_pattern()

    surface = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, cairo.Rectangle(0, 0, util.mm_to_pt(size[0]), util.mm_to_pt(size[1])))    
    ctx = cairo.Context(surface)
    ctx.push_group()
    ctx.set_source(pattern)
    ctx.paint()
    pattern2 = ctx.pop_group()

    if args.paper_size:
        if args.typ == "svg":
            print("ERROR: svg does not support multiple pages. Don't specify a paper size if you want to export svg file")
        if args.paper_size not in PAPER_SIZES.keys():
            print(args.paper_size)
            print("Known Paper Sizes:")
            print(PAPER_SIZES)
            return
        tiler = CairoTiler(pattern2, size, overlap=10, paper_size=PAPER_SIZES[args.paper_size])
        tiler.tile(args.output)
    else:
        if args.typ == "svg":
            surface = cairo.SVGSurface(args.output, util.mm_to_pt(size[0]), util.mm_to_pt(size[1]))
        elif args.typ == "pdf":
            surface = cairo.PDFSurface(args.output, util.mm_to_pt(size[0]), util.mm_to_pt(size[1]))

        ctx = cairo.Context(surface)
        ctx.set_source(pattern2)
        ctx.paint()


def spherical(args):
    chute = EllipticChutePattern(args.diameter,
                                 args.panels,
                                 args.excentricity,
                                 True,
                                 args.line_length if args.line_length else 2*args.diameter,
                                 args.spill_diameter if args.spill_diameter is not None else 0.1*args.diameter,
                                 args.grid)
    main(chute, args)

def toroidal(args):
    chute = ToroidalChutePattern(args.diameter,
                                 args.panels,
                                 args.form_factor,
                                 True,
                                 args.line_length if args.line_length else 2*args.diameter,
                                 args.spill_diameter,
                                 args.grid)
    main(chute, args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--paper_size")
    parser.add_argument("--panels", "-p", type=int, default=8)
    parser.add_argument("--grid", "-g", action="store_true")
    parser.add_argument("--typ", choices=["svg", "pdf"], default="pdf")
    subparser = parser.add_subparsers()

    sub_sphere = subparser.add_parser("spherical")
    sub_sphere.add_argument("--diameter", "-d", type = float, required=True)
    sub_sphere.add_argument("--tangent_lines, -t", action="store_true")
    sub_sphere.add_argument("--excentricity", "-e", type=float, default=0.7)
    sub_sphere.add_argument("--line_length", "-l", help="Line length. Default = 2 x diameter")
    sub_sphere.add_argument("--spill_diameter", "-s", type=float, help = "Diameter of spill hole. Default 0.1 x diameter")
    sub_sphere.set_defaults(func=spherical)

    sub_toroidal = subparser.add_parser("toroidal")
    sub_toroidal.add_argument("--diameter", "-d", type = float, required=True)
    sub_toroidal.add_argument("--tangent_lines, -t", action="store_false")
    sub_toroidal.add_argument("--form_factor", "-e", type=float, default=0.7)
    sub_toroidal.add_argument("--line_length", "-l", help="Line length. Default = 2 x diameter")
    sub_toroidal.add_argument("--spill_diameter", "-s", type=float)
    sub_toroidal.set_defaults(func=toroidal)
    args = parser.parse_args()
    args.func(args)
