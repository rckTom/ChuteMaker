from scipy import integrate
from ChutePattern import ChutePattern, MitreType
import numpy as np
import math

class EllipticChutePattern(ChutePattern):
    def __init__(self, diameter, num_panels, e, tangent_lines=True, line_length = None, spill_hole_diameter = None, grid=True, seam_allowance=(10,10,10,10)):
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

        super().__init__(grid, seam_allowance)

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