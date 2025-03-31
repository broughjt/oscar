from egraph_buddo1 import *
from itertools import chain
from pprint import pprint

x = Term("x", ())
sin_x = Term("sin", (x,))
cos_x = Term("cos", (x,))
one = Term(1, ())
zero = Term(0, ())
one_subtract_sin_divide_cos = Term("/", (
    Term("-", (one, sin_x)),
    cos_x
))
negate_sin_add_negate_negate_one_divide_cos_subtract_zero = Term("/", (
    Term("+", (Term("-", (sin_x,)), Term("-", (Term("-", (one,)),)))),
    Term("-", (cos_x, zero))
))
cos_divide_one_add_sin = Term("/", (cos_x, Term("+", (one, sin_x))))

g = EGraph()
# These should be equal right out the gate
a = g.add_term(one_subtract_sin_divide_cos)
b = g.add_term(negate_sin_add_negate_negate_one_divide_cos_subtract_zero)
c = g.add_term(cos_divide_one_add_sin)
g.rebuild()
print(g.find(a), g.find(b))
print(g.find(b), g.find(c))
k = 1

def compose(g, f):
    return lambda *xs: g(f(*xs))

def swap(t: tuple[Term, Term]) -> tuple[Term, Term]:
    l, r = t
    return (r, l)

def reverse(p: Callable[[EClassId, ...], tuple[Term, Term]]) \
        -> Callable[[EClassId, ...], tuple[Term, Term]]:
    return compose(swap, p)

divide_multiply = lambda x, y, w, z: (
    Term("/", (Term("*", (x, w)), Term("*", (y, z)))),
    Term("*", (Term("/", (x, y)), Term("/", (w, z))))
)
divide_self = lambda x, y: (
    Term("/", (x, y)),
    one
)


rules = [
    # (4, divide_multiply),
    # (4, reverse(divide_multiply)),
    (2, divide_self)
]

for i in range(1, k+1):
    # k = g.count_nodes()
    ms = list(chain.from_iterable((
        (t for t in g.ematch(n, r))
        for n, r in rules
    )))
    pprint(ms)
    # print(f"--------------- Iteration {i} ------------------")
    # pprint({a: e.nodes for a, e in g.classes.items()})
    # pprint(ms)
    
    for l, r in ms:
        print(l, r)
        id1 = g.add_pattern(l, hash_cons=False)
        id2 = g.add_pattern(r, hash_cons=False)
        g.union(id1, id2, hash_cons=False)
    g.rebuild()
        
    # if k == g.count_nodes():
    #     break
    # if g.find(id1) == g.find(id2):
    #     break

print(g.find(a), g.find(b))
print(g.find(b), g.find(c))

