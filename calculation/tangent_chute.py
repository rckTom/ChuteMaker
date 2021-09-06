import sympy as sp

a = sp.Symbol("a", positive=True, real=True)
b = sp.Symbol("b", positive=True, real=True)
x = sp.Symbol("x")
y = sp.Symbol("y")
t = sp.Symbol("t")
l = sp.Symbol("l")

r = sp.Symbol("r")
exc = sp.Symbol("exc")

a = r
b = exc * a
ellipse = sp.Eq(x**2/a**2 + y**2/b**2, 1)
fx = sp.solve(ellipse, y)[0]

m = sp.diff(fx, x)
gx = sp.Eq(fx, m*x+t)
ts = sp.solve(gx, t)[0]

x1 = 0
x2 = x
y1 = ts
y2 = m*x+ts

k = sp.Eq(l**2, (x2-x1)**2 + (y2-y1)**2)
sp.pprint(sp.solve(k, x))

sols = sp.solve(k, x)
sp.pprint(sp.simplify(sols[3]))

for sol in sols:
    radius = 1
    excentrity = 0.7
    length = 2

    print(sol.subs([(r, radius), (exc, excentrity), (l, length)]))