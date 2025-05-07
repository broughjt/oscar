from egraph_buddo4 import *

g = EGraph()

x = "x"
y = "y"
z = "z"
w = "w"

# add identity
# add associative
# add commutative
# add inverse
# subtract definition
# multiply identity
# multiply associative
# multiply commutative

x_id = g.add_term(TermNode(x, []))
y_id = g.add_term(TermNode(y, []))
zero = g.add_term(TermNode(0, []))
one = g.add_term(TermNode(1, []))

# 1. add identity
a0 = g.add_term(TermNode("+", [x, 0]))

# 2. add associative
a2 = g.add_term(TermNode("+", [TermNode("+", [x, y]), z]))
a3 = g.add_term(TermNode("+", [x, TermNode("+", [y, z])]))

# 3. add commutative
a4 = g.add_term(TermNode("+", [x, y]))
a5 = g.add_term(TermNode("+", [y, x]))

# 4. add inverse
a6 = g.add_term(TermNode("+", [x, TermNode("-", [x])]))

# 5. subtract definition
a7 = g.add_term(TermNode("+", [x, TermNode("-", [y])]))
a8 = g.add_term(TermNode("-", [x, y]))

# 6. multiply identity
a9 = g.add_term(TermNode("*", [x, 1]))

# 7. mutliply associative
a10 = g.add_term(TermNode("*", [TermNode("*", [x, y]), z]))
a11 = g.add_term(TermNode("*", [x, TermNode("*", [y, z])]))

# 8. multiply commutative
a12 = g.add_term(TermNode("*", [x, y]))
a13 = g.add_term(TermNode("*", [y, x]))

g.union(x_id, y_id)

g.rebuild()

for a, ns in g.classes.items():
    print(a, ns)

# print(f"add identity: {g.find(a0), g.find(x_id)}")
# print(f"add associative: {g.find(a2), g.find(a3)}")
# print(f"add commutative: {g.find(a4), g.find(a5)}")
# print(f"add inverse: {g.find(a6), g.find(zero)}")
# print(f"subtract definition: {g.find(a7), g.find(a8)}")
# print(f"multiply identity: {g.find(a9), g.find(x_id)}")
# print(f"multiply associative: {g.find(a10), g.find(a11)}")
# print(f"multiply commutative: {g.find(a12), g.find(a13)}")
