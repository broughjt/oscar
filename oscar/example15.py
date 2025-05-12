from egraph_buddo4 import *

import sympy

g = EGraph()

x = "x"
sin_x = TermNode("sin", [x])
cos_x = TermNode("cos", [x])
tan_x = TermNode("tan", [x])
tan_half_x = TermNode("tan", [TermNode("*", [x, TermNode("^-1", [2])])])
sin2_x = TermNode("*", [sin_x, sin_x])
cos2_x = TermNode("*", [cos_x, cos_x])
sin2_cos2 = TermNode("+", [sin2_x, cos2_x])
tan2_half_x = TermNode("*", [tan_half_x, tan_half_x])
one_add_cos = TermNode("+", [1, cos_x])
one_subtract_cos = TermNode("-", [1, cos_x])
sin_half_angle_numerator = TermNode("*", [2, tan_half_x])
sin_half_angle_denominator = TermNode("+", [1, tan2_half_x])
sin_half_angle = TermNode("*", [sin_half_angle_numerator, TermNode("^-1", [sin_half_angle_denominator])])
cos_half_angle_numerator = TermNode("-", [1, tan2_half_x])
cos_half_angle_denominator = TermNode("+", [1, tan2_half_x])
cos_half_angle = TermNode("*", [cos_half_angle_numerator, TermNode("^-1", [cos_half_angle_denominator])])
tan_half_angle_numerator = TermNode("*", [2, tan_half_x])
tan_half_angle_denominator = TermNode("-", [1, tan2_half_x])
tan_half_angle = TermNode("*", [tan_half_angle_numerator, TermNode("^-1", [tan_half_angle_denominator])])
tan_definition = TermNode("*", [sin_x, TermNode("^-1", [cos_x])])
first = TermNode("*", [one_subtract_cos, TermNode("^-1", [sin_x])])
second = TermNode("*", [sin_x, TermNode("^-1", [one_add_cos])])

ids = list(map(g.add_term, [
    sin_x,
    cos_x,
    tan_x,

    sin2_x,
    cos2_x,
    sin2_cos2,

    one_add_cos,
    one_subtract_cos,

    sin_half_angle,
    cos_half_angle,
    tan_definition,
    tan_half_angle,

    first,
    second,
    tan_half_x,
]))

# tangent definition
g.union(ids[2], ids[10])

# sin^2(x) + cos^2(x) = 1
g.union(ids[5], 1)

# Tangent half-angle formulas:
# sin(x) = (2*tan(x/2))/(1 + tan^2(x/2))
# cos(x) = (1-tan^2(x/2))/(1+tan^2(x/2))
g.union(ids[0], ids[8])
g.union(ids[1], ids[9])

g.rebuild()
first_id, second_id, third_id = ids[-3:]
fourth_id = ids[2]
fifth_id = ids[-4]

print(g.find(first_id), g.find(second_id), g.find(third_id))

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
    if g.find(first_id) == g.find(second_id) \
       and g.find(second_id) == g.find(third_id):
        print(f"breaking early on iteration {i}")
        break

for a, ns in g.classes.items():
    print(f"{a}:")
    for n in ns:
        print(f"  {n}")

print(g.find(first_id), g.find(second_id), g.find(third_id))
print(g.find(fourth_id), g.find(fifth_id))
