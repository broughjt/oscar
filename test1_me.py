from egraph_buddo2 import *

E = EGraph()
foobar = E.add_term(("foo", ("foo", ("bar",))))
bar = E.add_term(("bar",))
print(E)
E.union(foobar, bar)
E.rebuild()
print(E)
