from egraph_buddo3 import *

e = EGraph()
foobar = e.append_term(("foo", ("foo", ("bar",))))
print(e)
e.rewrite(1, lambda x: (("foo", x), 2*x))
print(e)
e.rebuild()
print(e)
