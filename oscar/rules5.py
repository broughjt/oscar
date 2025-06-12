from egraph_buddo4 import *

def reverse(r: Rule) -> Rule:
    return Rule(r.right, r.left)

x = PatternVariable("x")
y = PatternVariable("y")
z = PatternVariable("z")
w = PatternVariable("w")
i = PatternTerm("i", tuple())
two = PatternTerm(2, tuple())
sin_x = PatternTerm("sin", [x])
cos_x = PatternTerm("cos", [x])
exp_x = PatternTerm("exp", [x])
negate_x = PatternTerm("-", [x])
exp_negate_x = PatternTerm("exp", [negate_x])

sin_definition_n = PatternTerm("-", [exp_x, exp_negate_x])
sin_definition_d = PatternTerm("*", [two, i])
sin_definition_t = PatternTerm("/", [sin_definition_n, sin_definition_d])
cos_definition_n = PatternTerm("+", [exp_x, exp_negate_x])
cos_definition_d = two
cos_definition_t = PatternTerm("/", [cos_definition_n, cos_definition_d])

sin_definition = Rule(sin_x, sin_definition_t)
cos_definition = Rule(cos_x, cos_definition_t)
exp_reciprocal_definition = Rule(exp_x, PatternTerm("^-1", [exp_negate_x]))
divide_definition = Rule(
    PatternTerm("/", [x, y]),
    PatternTerm("*", [x, PatternTerm("^-1", [y])])
)
exp_add = Rule(
    PatternTerm("exp", [PatternTerm("+", [x, y])]),
    PatternTerm("*", [PatternTerm("exp", [x]), PatternTerm("exp", [y])])
)

rules = [
    sin_definition,
    cos_definition,
    exp_reciprocal_definition, reverse(exp_reciprocal_definition),
    divide_definition, reverse(divide_definition),
    exp_add, reverse(exp_add)
]
