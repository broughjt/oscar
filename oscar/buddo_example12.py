from egraph_buddo4 import *

import sympy

g = EGraph()

a = "a"
b = "b"
c = "c"
d = "d"
t0 = TermNode("*", [a, c])
t1 = TermNode("*", [TermNode("/", [a, b]), c])
t2 = TermNode("*", [t1, b])
t0_id = g.add_term(t0)
t1_id = g.add_term(t1)
b_id = g.add_term(b)
g.add_term(t2)

q0, r0 = sympy.div(t0_id, t1_id, *g.ids)
print(f"{g.find(t0_id)=}, {g.find(t1_id)=}, {g.find(q0)=}, {g.find(r0)=}")
q1, r1 = sympy.div(t0_id, b_id, *g.ids)
print(f"{g.find(t0_id)=}, {g.find(b_id)=}, {g.find(q1)=}, {g.find(r1)=}")
