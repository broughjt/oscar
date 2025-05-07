from egraph_buddo4 import *

import sympy

g = EGraph()

x = "x"
sin_x = TermNode("sin", [x])
cos_x = TermNode("cos", [x])
sin2_x = TermNode("*", [sin_x, sin_x])
cos2_x = TermNode("*", [cos_x, cos_x])
one_add_cos = TermNode("+", [1, cos_x])
one_subtract_cos = TermNode("-", [1, cos_x])
foo = TermNode("*", [one_add_cos, one_subtract_cos])
bar = TermNode("*", [TermNode("/", [one_subtract_cos, sin_x]), one_add_cos])
baz = TermNode("*", [bar, sin_x])

a3 = g.add_term(sin_x)
g.add_term(cos_x)
g.add_term(sin2_x)
g.add_term(cos2_x)
a1 = g.add_term(one_add_cos)
a0 = g.add_term(one_subtract_cos)
b0 = g.add_term(foo)
a2 = g.add_term(bar)
g.add_term(baz)

g.rebuild()

q, r = sympy.div(b0, a2, *g.ids)
print(f"{g.find(b0)=}, {g.find(a2)=}, {g.find(q)=}, {g.find(r)=}")
