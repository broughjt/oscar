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
# one_subtract_sin_divide_cos = TermNode("/", [
#     TermNode("-", [1, sin_x]),
#     cos_x
# ])
# cos_divide_one_add_sin = TermNode("/", [
#     cos_x,
#     TermNode("+", [1, sin_x])
# ])
one_subtract_cos = TermNode("-", [1, cos_x])
one_add_cos = TermNode("+", [1, cos_x])
quux = TermNode("/", [one_subtract_cos, sin_x])
foo = TermNode("*", [quux, one_add_cos])
bar = TermNode("*", [foo, sin_x])
baz = TermNode("*", [one_subtract_cos, one_add_cos])

g = EGraph()

a0 = g.add_term(sin2_cos2)
a1 = g.add_term(1)
g.union(a0, a1)

a2 = g.add_term(sin_x)
a3 = g.add_term(cos_x)
a4 = g.add_term(one_subtract_cos)
a5 = g.add_term(one_add_cos)
a6 = g.add_term(foo) # ((1 - cos(x))/sin(x)) * (1 + cos(x))
a7 = g.add_term(bar) # ((1 - cos(x))/sin(x)) * (1 + cos(x)) * sin(x)
a8 = g.add_term(baz) # (1 - cos(x)) * (1 + cos(x))
g.add_term(TermNode("*", [quux, sin_x]))
b0 = g.add_term(TermNode("/", [baz, sin_x]))
g.rebuild()

# q, r = sympy.div(g.find(a8), g.find(a6))
# print(g.find(a4), g.find(a5))
# print(g.find(a8), g.find(a6), g.find(q), g.find(r))

for i in range(1, 101):
    k = g.count_nodes()
    print(f"------------------------------------------------- {i}, {k} ----------------------------")
    for a, c in g.classes.items():
        print(a, c)

    matches = set()
    for a in g.classes.keys():
        for b in g.classes.keys():
            q, r = sympy.div(a, b, g.ids)
            if g.find(r) == 0:
                matches.add((a, b, g.find(q)))
    print("matches:")
    for m in matches:
        print(m)
    for a, b, q in matches:
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


print("overall: ", g.find(a6), g.find(a2))
print("equation: ", g.find(a8), g.find(a7))
print("step: ", g.find(a6), g.find(b0))
