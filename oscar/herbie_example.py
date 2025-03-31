from egraph import *
from herbie_rules import rules

one = Term("1", tuple())
x = Term("x", tuple())
sin_x = Term("sin", (x,))
cos_x = Term("cos", (x,))
one_subtract_sin_divide_cos = Term("/", (Term("-", (one, sin_x)), cos_x))
cos_divide_one_add_sin = Term("/", (cos_x, Term("+", (one, sin_x))))

g = EGraph()
id1 = g.add_term(one_subtract_sin_divide_cos)
id2 = g.add_term(cos_divide_one_add_sin)
print(g.find(id1), g.find(id2))
g.rebuild()
l = 20

for i in range(1, l+1):
    k = g.count_nodes()
    ms = list(chain.from_iterable((
        ((r, s, a) for (s, a) in g.ematch(r.left))
        for r in rules
    )))
    print(f"--------------- Iteration {i} ------------------")
    pprint({a: e.nodes for a, e in g.classes.items()})
    pprint(ms)
    
    for (r, s, a) in ms:
        b = g.substitute_add(r.right, s)
        g.union(a, b)
    g.rebuild()
        
    if k == g.count_nodes():
        break
    if g.find(id1) == g.find(id2):
        break

print(f"finished after {i} iterations")
pprint({a: e.nodes for a, e in g.classes.items()})
print(g.find(id1), g.find(id2))
