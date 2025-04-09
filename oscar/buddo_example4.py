from egraph_buddo4 import *

x = "x"
sin_x = TermNode("sin", (x,))
cos_x = TermNode("cos", (x,))
sin2_x = TermNode("*", [sin_x, sin_x])
cos2_x = TermNode("*", [cos_x, cos_x])
sin2_cos2 = TermNode("+", [sin2_x, cos2_x])
g = EGraph()

a1 = g.add_term(sin2_cos2)
a5 = g.add_term(TermNode("+", [sin2_x, TermNode("+", [0, TermNode("*", [cos2_x, 1])])]))
a6 = g.add_term(TermNode("+", [cos2_x, sin2_x]))
print(g.find(a1), g.find(a5))
print(g.find(a5), g.find(a6))
a2 = g.add_term(1)
a3 = g.add_term(sin2_x)
a4 = g.add_term(TermNode("-", [1, cos2_x]))
g.union(a1, a2)
g.rebuild()
print(g.find(a3) == g.find(a4))
print(g.find(a1), g.find(a5))
