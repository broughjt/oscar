from egraph_buddo4 import *
from rules4 import rules
from itertools import chain

import sympy

g = EGraph()

x = "x"
sin_x = TermNode("sin", (x,))
cos_x = TermNode("cos", (x,))
sin2_x = TermNode("*", [sin_x, sin_x])
cos2_x = TermNode("*", [cos_x, cos_x])
sin2_cos2 = TermNode("+", [sin2_x, cos2_x])
one_add_cos = TermNode("+", [1, cos_x])
one_subtract_cos = TermNode("-", [1, cos_x])
one_add_sin = TermNode("+", [1, sin_x])
one_subtract_sin = TermNode("-", [1, sin_x])
foo = TermNode("/", [one_subtract_cos, sin_x])
bar = TermNode("*", [foo, one_add_cos])
baz = TermNode("/", [one_subtract_sin, cos_x])
buzz = TermNode("/", [cos_x, one_add_sin])
quux = TermNode("*", [baz, TermNode("/", [one_add_sin, one_add_sin])])

# g.add_term(x)
# b0 = g.add_term(sin_x)
# g.add_term(cos_x)
a0 = g.add_term(sin2_cos2)
# g.add_term(one_add_cos)
# g.add_term(one_subtract_cos)
# g.add_term(foo)
# b1 = g.add_term(bar)
c0 = g.add_term(baz)
c1 = g.add_term(buzz)
g.add_term(quux)
# d0 = g.add_term(TermNode("-", [1, sin2_x]))
# d1 = g.add_term(TermNode("*", [cos_x, cos_x]))

g.rebuild()

# print(g.find(b0), g.find(b1))
print(g.find(c0), g.find(c1))

for i in range(1, 1000+1):
    k = g.count_nodes()
    ms = list(chain.from_iterable((
        ((r, s, a) for (s, a) in g.ematch(r.left))
        for r in rules
    )))
    print(i, k)
                    
    for (r, s, a) in ms:
        b = g.substitute_add(r.right, s)
        g.union(a, b)
    g.rebuild()

    if k == g.count_nodes():
        print(f"saturated after {i} iterations")
        break
    if g.find(c0) == g.find(c1):
        print(f"breaking early on iteration {i}, c0 == c1")
        break

# print(g.find(b0), g.find(b1))
print(g.find(c0), g.find(c1))
# print(g.find(d0), g.find(d1))

for a, ns in g.classes.items():
    print(a, "   ", ns)
    
