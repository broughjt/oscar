from egraph import *

# Example from the docs.rs page for egg
# https://docs.rs/egg/latest/egg/index.html

commute_add = Rule(
    PatternTerm("+", [PatternVariable("a"), PatternVariable("b")]),
    PatternTerm("+", [PatternVariable("b"), PatternVariable("a")])
)
commute_multiply = Rule(
    PatternTerm("*", [PatternVariable("a"), PatternVariable("b")]),
    PatternTerm("*", [PatternVariable("b"), PatternVariable("a")])
)
add_identity = Rule(
    PatternTerm("+", [PatternVariable("a"), PatternTerm("0", list())]),
    PatternVariable("a")
)
multiply_annihilator = Rule(
    PatternTerm("*", [PatternVariable("a"), PatternTerm("0", list())]),
    PatternTerm("0", list())
)
multiply_identity = Rule(
    PatternTerm("*", [PatternVariable("a"), PatternTerm("1", list())]),
    PatternVariable("a")
)
rules = [
    commute_add, commute_multiply,
    add_identity,
    multiply_annihilator, multiply_identity
]

g = EGraph()
foo = Term("foo", tuple())
one = Term("1", tuple())
zero = Term("0", tuple())
fourty_two = Term("42", tuple())
term1 = Term("+", (zero, Term("*", (one, foo))))
term2 = Term("*", (zero, fourty_two))
foo_id = g.add_term(foo)
one_id = g.add_term(one)
zero_id = g.add_term(zero)
term1_id = g.add_term(term1)
term2_id = g.add_term(term2)
print(g.find(foo_id) == g.find(term1_id))
print(g.find(zero_id) == g.find(term2_id))
print(g.find(one_id) == g.find(zero_id))
g.rebuild()
i = g.run(rules)
print(f"finished after {i} iterations")

print(g.find(foo_id) == g.find(term1_id))
print(g.find(zero_id) == g.find(term2_id))
print(g.find(one_id) == g.find(zero_id))

print("We can do the egg example!")
