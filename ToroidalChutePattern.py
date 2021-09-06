import cairo
import math
import numpy as np
import scipy.integrate as integrate
from ChutePattern import ChutePattern

class ToroidalChutePattern(ChutePattern):
    def __init__(self, diameter, num_panels, e, tangent_lines=True, line_length = None, spill_hole_diameter = 0, grid=True, seam_allowance=(10,10,10,10)):
        self.line_length = line_length
        self.r = diameter/4 * e
        self.rt = diameter/2 - self.r
        self.rs = spill_hole_diameter/2
        self.num_panels = num_panels
        self.tangent_lines = tangent_lines
        super().__init__(grid, seam_allowance)

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