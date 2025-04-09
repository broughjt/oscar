from egraph_buddo4 import *
from pprint import pprint
from pyrsistent import pbag

import sympy
import itertools

x = "x"
sin_x = TermNode("sin", (x,))
cos_x = TermNode("cos", (x,))
sin2_x = TermNode("*", [sin_x, sin_x])
cos2_x = TermNode("*", [cos_x, cos_x])
sin2_cos2 = TermNode("+", [sin2_x, cos2_x])
one_minus_sin_divide_cos = TermNode("/", [
    TermNode("-", [1, sin_x]),
    cos_x
])
cos_divide_one_add_sin = TermNode("/", [
    cos_x,
    TermNode("+", [1, sin_x])
])
one_subtract_cos = TermNode("-", [1, cos_x])
one_add_cos = TermNode("+", [1, cos_x])

g = EGraph()

a0 = g.add_term(sin2_cos2)
a1 = g.add_term(1)
g.union(a0, a1)

a2 = g.add_term(sin_x)
a3 = g.add_term(cos_x)
a4 = g.add_term(one_subtract_cos)
a5 = g.add_term(one_add_cos)
a6 = g.add_term(TermNode("*", [
    TermNode("/", [one_subtract_cos, sin_x]),
    one_add_cos
]))
a7 = g.add_term(one_minus_sin_divide_cos)
a8 = g.add_term(cos_divide_one_add_sin)
g.rebuild()

for i in range(1, 1_001):
    k = g.count_nodes()

    matches = set()
    for a in g.classes.keys():
        for b in g.classes.keys():
            q, r = sympy.div(a, b, g.ids)
            if g.find(r) == 0 and a != 1 and b != 1 and a != b:
                matches.add((a, pbag([b, g.find(q)])))

    for a, bq in matches:
        b, q = list(bq)
        c = g.add(ENode("/", [a, b]))
        d = g.add(ENode("/", [a, q]))
        g.union(c, q)
        g.union(d, b)
    g.rebuild()

    if k == g.count_nodes():
        print(f"saturated after {i} iterations")
        break

for a, ns in g.classes.items():
    print(a, "   ", ns)
