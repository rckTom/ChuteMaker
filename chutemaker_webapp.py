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

from CairoTiler import PAPER_SIZES, CairoTiler
from flask import Flask, render_template, request, Response, send_file
from util import mm_to_pt
import cairo
import io
from EllipticalChutePattern import EllipticChutePattern
from ToroidalChutePattern import ToroidalChutePattern
from ChutePattern import MitreType

DEBUG = True
app = Flask(__name__)

STATIC_CONTEXT = {
    "paper_sizes": PAPER_SIZES
}


def generateSVG(pattern, size):
    f = io.BytesIO()

    surface = cairo.SVGSurface(f, mm_to_pt(size[0]), mm_to_pt(size[1]))
    ctx = cairo.Context(surface)

    ctx.set_source(pattern)
    ctx.paint()

    surface.finish()
    f.seek(0)
    return f


def generatePDF(pattern, size, tiling=False, paper_size="A4", margin=10):
    f = io.BytesIO()

    if not tiling:
        surface = cairo.PDFSurface(f, mm_to_pt(size[0]), mm_to_pt(size[1]))
        ctx = cairo.Context(surface)

        ctx.set_source(pattern)
        ctx.paint()
        surface.finish()
    else:
        tiler = CairoTiler(pattern, size, PAPER_SIZES[paper_size],
                           (margin, margin, margin, margin))
        tiler.tile(f)

    f.seek(0)

    return f


@app.route("/generate", methods=["POST"])
def spherical():
    if request.method == "POST":
        diameter = request.form.get("diameter")
        spill_diameter = request.form.get("spillDiameter")
        e = request.form.get("e")
        panels = request.form.get("panels")
        tangentLines = request.form.get("tangentLines")
        jointStyle = request.form.get("jointStyle")
        line_length = request.form.get("lineLength")
        tiling = request.form.get("tiling")
        paper_size = request.form.get("paperSize")
        margin = request.form.get("paperMargin")
        fileType = request.form.get("typeSelect")
        seamAllowance = request.form.get("seamAllowance")
        grid = request.form.get("grid")
        chute_type = request.form.get("type")

        if any(
                v is None for v in
            [diameter, spill_diameter, e, panels, jointStyle, seamAllowance]):
            return Response(status=502)

        diameter = float(diameter)
        spill_diameter = float(spill_diameter)
        e = float(e)
        panels = int(panels)
        seamAllowance = float(seamAllowance)

        grid = grid is not None

        if tangentLines is not None:
            tangentLines = bool(tangentLines)
        else:
            tangentLines = False

        if tangentLines and line_length is not None:
            line_length = float(line_length)
            tangentLines = True
        else:
            line_length = 2 * diameter
            tangentLines = False

        if not any([v is None for v in [tiling, paper_size, margin]]):
            tiling = bool(tiling)
            margin = float(margin)
        else:
            tiling = False

        if jointStyle == "selectMitre":
            jointStyle = MitreType.miter
        elif jointStyle == "selectNone":
            jointStyle = MitreType.none
        else:
            jointStyle = MitreType.bevel

        try:
            if chute_type == "hemispherical":
                cp = EllipticChutePattern(
                    diameter,
                    panels,
                    e,
                    tangentLines,
                    line_length,
                    spill_diameter,
                    grid=grid,
                    seam_allowance=(seamAllowance, seamAllowance,
                                    seamAllowance, seamAllowance))
            elif chute_type == "toroidal":
                cp = ToroidalChutePattern(
                    diameter,
                    panels,
                    e,
                    tangentLines,
                    line_length,
                    spill_diameter,
                    grid,
                    seam_allowance=(seamAllowance, seamAllowance,
                                    seamAllowance, seamAllowance))
            cp.set_joint_style(jointStyle)
        except Exception as e:
            print(e)
            return Response(status=502)

        pattern, size = cp.get_pattern()

        if fileType == "svg":
            f = generateSVG(pattern, size)
            mime = "image/svg"
            ext = ".svg"
        elif fileType == "pdf":
            f = generatePDF(pattern, size, tiling, paper_size, margin)
            mime = "application/pdf"
            ext = ".pdf"
        else:
            return Response(status=400)

        return send_file(f,
                         mimetype=mime,
                         download_name=chute_type + ext,
                         as_attachment=True)

@app.route("/")
def index():
    return render_template("selector.html", static = STATIC_CONTEXT)


@app.route("/h")
def hemisperhical_chute():
    return render_template("hemispherical.html", static = STATIC_CONTEXT)


@app.route("/t")
def toroidal_chute():
    return render_template("toroidal.html", static = STATIC_CONTEXT)


if __name__ == "__main__":
    app.run("localhost", port=8080, debug=DEBUG)
