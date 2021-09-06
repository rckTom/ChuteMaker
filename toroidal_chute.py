import sympy as sp

r = sp.Symbol("r")
rt = sp.Symbol("rt")
x = sp.Symbol("x")
y = sp.Symbol("y")
t = sp.Symbol("t")
l = sp.Symbol("l")


f = sp.Eq(r**2, (x-rt)**2 + y**2)
f = sp.solve(f, y)[0]
m = sp.diff(f, x)
g = sp.diff(f, x) * x + t
ts = sp.solve(g, t)[0]

x1 = 0
y1 = ts
x2 = x
y2 = m*x+ts

k = sp.Eq(l**2, (x2-x1)**2 + (y2-y1)**2)
sols = sp.solve(k, x)

radius = 500
radiust = 550
length = 2000

print(sols)

for sol in sols:
    print(float(sol.subs([(r, radius), (rt, radiust), (l, length)])))
