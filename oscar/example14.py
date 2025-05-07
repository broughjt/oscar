from egraph_buddo4 import *

import sympy

g = EGraph()

x = "x"
sin_x = TermNode("sin", [x])
cos_x = TermNode("cos", [x])
sin2_x = TermNode("*", [sin_x, sin_x])
cos2_x = TermNode("*", [cos_x, cos_x])
sin2_cos2 = TermNode("+", [sin2_x, cos2_x])
one_add_cos = TermNode("+", [1, cos_x])
one_subtract_cos = TermNode("-", [1, cos_x])
foo = TermNode("*", [one_subtract_cos, TermNode("^-1", [sin_x])])
bar = TermNode("*", [sin_x, TermNode("^-1", [one_add_cos])])

ids = list(map(g.add_term, [
    sin_x, # 0
    cos_x, # 1
    sin2_x, # 2
    cos2_x, # 3
    sin2_cos2, # 4
    one_add_cos, # 5 
    one_subtract_cos, # 6
    foo, # 7
    bar # 8
]))
print(ids)

g.union(ids[4], 1)
g.rebuild()

print(g.find(ids[7]), g.find(ids[8]))

for i in range(1, 1+1):
    print(f"iteration {i}")
    for a, ns in g.classes.items():
        print(f"{a}:")
        for n in ns:
            print(f"  {n}")
    k = g.count_nodes()
    for a in g.classes.keys():
        a = g.find(a)

        # x != 0 => x * x^-1 = 1
        if a != 0:
            b = g.add(ENode("^-1", [a]))
            c = g.add(ENode("*", [a, b]))
            g.union(c, 1)
    g.rebuild()

    if k == g.count_nodes():
        print(f"saturated after {i} iterations")
        break
    if g.find(ids[7]) == g.find(ids[8]):
        print(f"breaking early on iteration {i}")
        break

for a, ns in g.classes.items():
    print(f"{a}:")
    for n in ns:
        print(f"  {n}")

b0 = g.add_term(TermNode("*", [one_subtract_cos, TermNode("*", [one_add_cos, TermNode("^-1", [one_add_cos])])]))
print("Step 1:", g.find(b0), g.find(ids[6]))
b1 = g.add_term(TermNode("*", [sin2_x, TermNode("^-1", [one_add_cos])]))
print("Step 2:", g.find(b0), g.find(b1))

print("Final:", g.find(ids[7]), g.find(ids[8]), g.find(ids[7]) == g.find(ids[8]))
