from egraph_buddo2 import *

E = EGraph()
foobar = E.append_term(("foo", ("foo", ("bar",))))
bar = E.append_term(("bar",))
print(E)
E.union(foobar, bar)
E.rebuild()
print(E)
E.union(bar * bar, foobar)
E.rebuild()
print(E)
