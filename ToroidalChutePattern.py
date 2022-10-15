import cairo
import math
import numpy as np
import scipy.integrate as integrate
from ChutePattern import ChutePattern

class ToroidalChutePattern(ChutePattern):
    def __init__(self, diameter, num_panels, e, tangent_lines=True, line_length = None, spill_hole_diameter = 0, grid=True, seam_allowance=(10,10,10,10)):
        self.line_length = line_length
        self.diameter = diameter
        self.spill_diamter = spill_hole_diameter
        self.e = e
        self.r = diameter/4 * e
        self.rt = diameter/2 - self.r
        self.rs = spill_hole_diameter/2
        self.num_panels = num_panels
        self.tangent_lines = tangent_lines
        super().__init__(grid, seam_allowance)

        self.line_lengths = dict()
        self.line_lengths["A"] = self.line_length
        self.calc_line_lenghts()

    def description(self):
        return {
            "diameter": self.diameter,
            "panels": self.num_panels,
            "spill hole diameter": self.rs * 2,
            "form factor": self.e,
            "line length": "n/a" if not self.tangent_lines else f"A: {self.line_length:.0f}, B: {self.line_lengths['B']:.0f}, C: {self.line_lengths['C']:.0f}",
            "seam allowance": self.seam_allowance
        }

    def _t(self, x):
        return math.acos((x-self.rt)/self.r)

    def _x(self, t):
        return self.rt + math.cos(t) * self.r

    def _y(self, t):
        return math.sin(t) * self.r

    def _tangential_line_point(self):
        l = self.line_length
        r = self.r
        rt = self.rt
        x = l*(l*rt + r*math.sqrt(l**2 + r**2 - rt**2))/(l**2 + r**2)
        return self._t(x)

    def get_spill_diameter(self):
        minx = self.rt - self.r

        if (minx > self.rs):
            rs = minx
            print("WARNING: spill hole to small. Extend it to minimal possible size")
        elif (self.rs >= self.rt):
            print("WARNING: spill hole diameter to large. Scaling it down")
            rs = self.rt
        else:
            rs = self.rs
        
        return rs

    def calc_line_lenghts(self):
        la = 0
        lb = 0

        rs = self.get_spill_diameter()

        tmin = -self._tangential_line_point()
        tmax = self._t(rs)

        xa1 = self._x(tmin)
        ya1 = self._y(tmin)
        m = math.tan(tmin + math.pi/2)
        xa2 = 0
        ya2 = ya1 - m * xa1

        print(f"A1: x {xa1}, y {ya1}")
        print(f"A2: x {xa2}, y {ya2}")

        if tmax < math.pi and tmax > math.pi/2:
            xb1 = self._x(tmax)
            yb1 = self._y(tmax)
            m = math.tan(tmax - math.pi/2)

            xb2 = 0
            yb2 = yb1 - m * xb1

            lb = math.sqrt((xb1 - xb2)**2 + (yb1 - yb2)**2)
            lc = math.sqrt((yb2 - ya2)**2)

        self.line_lengths["B"] = lb
        self.line_lengths["C"] = lc

    def _get_pattern_path(self):
        rs = self.get_spill_diameter()

        tmin = 0
        
        if self.tangent_lines:
            tmin = -self._tangential_line_point()

        tmax = self._t(rs)
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
