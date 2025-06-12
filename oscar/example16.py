from egraph_buddo4 import *

import sympy
from rules5 import rules

g = EGraph()

x = "x"
i = "i"
sin_x = TermNode("sin", [x])
cos_x = TermNode("cos", [x])
exp_x = TermNode("exp", [x])
sin2_x = TermNode("*", [sin_x, sin_x])
cos2_x = TermNode("*", [cos_x, cos_x])
sin2_cos2_x = TermNode("+", [sin2_x, cos2_x])

i2 = TermNode("*", [i, i])
exp_0 = TermNode("exp", [0])

# i*i = -1
# sin(x) = (exp(x) - exp(-x)) / 2*i
# cos(x) = (exp(x) + exp(-x)) / 2
# tan(x) = sin(x)/cos(x)

# x * x^-1 = 1
# exp(x + y) = exp(x) * exp(y)
# exp(x) = exp(-x)^-1

ids = list(map(g.add_term, [
    sin_x,
    cos_x,

    i2,
    exp_0,

    sin2_x,
    cos2_x,
    sin2_cos2_x,
]))

g.union(ids[2], -1)
g.union(ids[3], 1)
g.rebuild()

print(g.find(ids[-1]), 1)

for i in range(1, 10+1):
    print(f"iteration {i}")
    for a, ns in g.classes.items():
        print(f"{a}:")
        for n in ns:
            print(f"  {n}")

    k = g.count_nodes()

    ms = list(chain.from_iterable((
        ((r, s, a) for (s, a) in g.ematch(r.left))
        for r in rules
    )))

    for a in g.classes.keys():
        a = g.find(a)

        # x != 0 => x * x^-1 = 1
        if a != 0:
            b = g.add(ENode("^-1", [a]))
            c = g.add(ENode("*", [a, b]))
            g.union(c, 1)
    for (r, s, a) in ms:
        b = g.substitute_add(r.right, s)
        g.union(a, b)
    g.rebuild()

    if k == g.count_nodes():
        print(f"saturated after {i} iterations")
        break
    if g.find(ids[-1]) == 1:
        print(f"breaking early on iteration {i}")
        break

for a, ns in g.classes.items():
    print(f"{a}:")
    for n in ns:
        print(f"  {n}")
print(g.find(ids[-1]), 1)
