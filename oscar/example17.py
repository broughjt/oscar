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

tan_x = TermNode("tan", [x])
tan_half_x = TermNode("tan", [TermNode("/", [x, 2])])
tan2_half_x = TermNode("*", [tan_half_x, tan_half_x])
tan_definition = TermNode("/", [sin_x, cos_x])

sin_half_angle_numerator = TermNode("*", [2, tan_half_x])
sin_half_angle_denominator = TermNode("+", [1, tan2_half_x])
sin_half_angle = TermNode("/", [sin_half_angle_numerator, sin_half_angle_denominator])
cos_half_angle_numerator = TermNode("-", [1, tan2_half_x])
cos_half_angle_denominator = TermNode("+", [1, tan2_half_x])
cos_half_angle = TermNode("/", [cos_half_angle_numerator, cos_half_angle_denominator])
tan_half_angle_numerator = TermNode("*", [2, tan_half_x])
tan_half_angle_denominator = TermNode("-", [1, tan2_half_x])
tan_half_angle = TermNode("/", [tan_half_angle_numerator, tan_half_angle_denominator])

# i*i = -1
# sin(x) = (exp(x) - exp(-x)) / 2*i
# cos(x) = (exp(x) + exp(-x)) / 2
# tan(x) = sin(x)/cos(x)

# x * x^-1 = 1
# exp(x + y) = exp(x) * exp(y)
# exp(x) = exp(-x)^-1

sin_id = g.add_term(sin_x)
cos_id = g.add_term(cos_x)
tan_id = g.add_term(tan_x)
i2_id = g.add_term(i2)
exp_0_id = g.add_term(exp_0)
tan_definition_id = g.add_term(tan_definition)
sin2_cos2_id = g.add_term(sin2_cos2_x)
sin_half_angle_id = g.add_term(sin_half_angle)
cos_half_angle_id = g.add_term(cos_half_angle)
tan_half_angle_id = g.add_term(tan_half_angle)

g.union(i2_id, -1)
g.union(exp_0_id, 1)
g.union(tan_id, tan_definition_id)
g.rebuild()

print(f"{g.find(sin2_cos2_id)=}", 1)
print(f"{g.find(sin_id)=}, {g.find(sin_half_angle_id)=}")
print(f"{g.find(cos_id)=}, {g.find(cos_half_angle_id)=}")
print(f"{g.find(tan_id)=}, {g.find(tan_half_angle_id)=}")

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
    if g.find(sin2_cos2_id) == 1 \
       and g.find(sin_id) == g.find(sin_half_angle_id) \
       and g.find(cos_id) == g.find(cos_half_angle_id) \
       and g.find(tan_id) == g.find(tan_half_angle_id):
        print(f"breaking early on iteration {i}")
        break

for a, ns in g.classes.items():
    print(f"{a}:")
    for n in ns:
        print(f"  {n}")
print(f"{g.find(sin2_cos2_id)=}", 1)
print(f"{g.find(sin_id)=}, {g.find(sin_half_angle_id)=}")
print(f"{g.find(cos_id)=}, {g.find(cos_half_angle_id)=}")
print(f"{g.find(tan_id)=}, {g.find(tan_half_angle_id)=}")
