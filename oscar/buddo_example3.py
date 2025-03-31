from egraph_buddo3 import *
from rules3 import rules

x = "x"
sin_x = TermNode("sin", (x,))
cos_x = TermNode("cos", (x,))
sin2_cos2 = TermNode("+", [
    TermNode("*", [sin_x, sin_x]),
    TermNode("*", [cos_x, cos_x]),
])
one_subtract_sin_divide_cos = TermNode("/", (
    TermNode("-", (1, sin_x)),
    cos_x
))
negate_sin_add_negate_negate_one_divide_cos_subtract_zero = TermNode("/", (
    TermNode("+", (TermNode("-", (sin_x,)), TermNode("-", (TermNode("-", (1,)),)))),
    TermNode("-", (cos_x, 0))
))
cos_divide_one_add_sin = TermNode("/", (cos_x, TermNode("+", (1, sin_x))))

g = EGraph()
one_id = g.add_term(one_subtract_sin_divide_cos)
two_id = g.add_term(negate_sin_add_negate_negate_one_divide_cos_subtract_zero)
three_id = g.add_term(cos_divide_one_add_sin)
g.add_term(sin2_cos2)
g.rebuild()
print(g.find(one_id), g.find(two_id), g.find(one_id) == g.find(two_id))
print(g.find(one_id), g.find(three_id), g.find(one_id) == g.find(three_id))
l = 1_000_000

for i in range(1, l+1):
    k = g.count_nodes()
    ms = list(chain.from_iterable((
        ((r, s, a) for (s, a) in g.ematch(r.left))
        for r in rules
    )))
    print(i)
                    
    for (r, s, a) in ms:
        b = g.substitute_add(r.right, s)
        g.union(a, b)

    if k == g.count_nodes():
        break
    if g.find(one_id) == g.find(three_id):
        break

print(g.find(one_id), g.find(two_id), g.find(one_id) == g.find(two_id))
print(g.find(one_id), g.find(three_id), g.find(one_id) == g.find(three_id))
