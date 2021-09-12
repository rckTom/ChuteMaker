from flask import Flask, render_template, request, Response, send_file
from util import mm_to_pt
import cairo
import flask
import io
from EllipticalChutePattern import EllipticChutePattern
from ToroidalChutePattern import ToroidalChutePattern
from ChutePattern import MitreType

DEBUG=True
app = Flask(__name__)

def generateSVG(pattern, size):
    f = io.BytesIO()
    
    surface = cairo.SVGSurface(f, mm_to_pt(size[0]), mm_to_pt(size[1]))
    ctx = cairo.Context(surface)

    ctx.set_source(pattern)
    ctx.paint()
    
    surface.finish()
    f.seek(0)
    return f


def generatePDF(pattern):
    pass

@app.route("/spherical", methods=["POST"])
def spherical():
    if request.method == "POST":
        print(request.form.keys())
        diameter = request.form.get("diameter")
        spill_diameter = request.form.get("spillDiameter")
        e = request.form.get("e")
        panels = request.form.get("panels")
        tangentLines = request.form.get("tangentLines")
        jointStyle = request.form.get("jointStyle")
        line_length = request.form.get("lineLength")

        if any(v is None for v in [diameter, spill_diameter, e, panels, jointStyle]):
            return Response(status=502)

        diameter = float(diameter)
        spill_diameter = float(spill_diameter)
        e = float(e)
        panels = int(panels)

        if tangentLines is not None:
            tangentLines = bool(tangentLines)
        else:
            tangentLines = False

        print(tangentLines)
        print(line_length)

        if tangentLines and line_length is not None:
            line_length = float(line_length)
            tangentLines = True
        else:
            line_length = 2*diameter
            tangentLines = False

        if  jointStyle == "selectMitre":
            jointStyle = MitreType.miter
        elif jointStyle == "selectNone":
            jointStyle = MitreType.none
        else:
            jointStyle = MitreType.bevel

        try:
            cp = EllipticChutePattern(diameter, panels, e, tangentLines, line_length, spill_diameter, grid=True)
            cp.set_joint_style(jointStyle)
        except:
            return Response(status=502)

        pattern, size = cp.get_pattern()
        svg = generateSVG(pattern, size)
        return send_file(svg, mimetype="image/svg", attachment_filename="spherical.svg", as_attachment=True)

@app.route("/toroidal", methods=["POST"])
def toroidal():
    if request.method == "POST":
        print(request.form.keys())
        diameter = float(request.form.get("diameter"))
        spill_diameter = float(request.form.get("spillDiameter"))
        e = float(request.form.get("e"))
        panels = int(request.form.get("panels"))
        tangentLines = request.form.get("tangentLines")

        if not tangentLines:
            line_length = float(request.form.get("lineLength"))
            tangentLines = True
        else:
            line_length = 2*diameter
            tangentLines = False

        try:
            cp = ToroidalChutePattern(diameter, panels, e, tangentLines, line_length, spill_diameter)
        except:
            return Response(status=502)

        pattern, size = cp.get_pattern()
        svg = generateSVG(pattern, size)
        return send_file(svg, mimetype="image/svg", attachment_filename="toroidal.svg", as_attachment=True)


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run("localhost", port = 8080, debug=DEBUG)