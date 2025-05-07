from egraph_buddo4 import *

x = PatternVariable("x")
y = PatternVariable("y")
z = PatternVariable("z")
w = PatternVariable("w")
zero = PatternTerm(0, tuple())
one = PatternTerm(1, tuple())
cos_x = PatternTerm("cos", [x])
sin_x = PatternTerm("sin", [x])
sin2_x = PatternTerm("*", [sin_x, sin_x])
cos2_x = PatternTerm("*", [cos_x, cos_x])

def reverse(r: Rule) -> Rule:
    return Rule(r.right, r.left)

divide_self_equal_one = Rule(
    PatternTerm("/", [x, x]),
    one
)
divide_multiply = Rule(
    PatternTerm("*", [PatternTerm("/", [x, y]), z]),
    PatternTerm("/", [PatternTerm("*", [x, z]), y])
)
sin2_cos2_equal_one = Rule(
    PatternTerm("+", [sin2_x, cos2_x]),
    one
)
multiply_divide_equal_divide_multiply = Rule(
    PatternTerm("/", [PatternTerm("*", [x, w]), PatternTerm("*", [y, z])]),
    PatternTerm("*", [PatternTerm("/", [x, y]), PatternTerm("/", [w, z])])
)

rules = [
    divide_self_equal_one,
    divide_multiply, reverse(divide_multiply),
    multiply_divide_equal_divide_multiply, reverse(multiply_divide_equal_divide_multiply),
    sin2_cos2_equal_one
]
