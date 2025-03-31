from egraph_buddo3 import *

x = PatternVariable("x")
y = PatternVariable("y")
z = PatternVariable("z")
w = PatternVariable("w")
zero = PatternTerm(0, tuple())
one = PatternTerm(1, tuple())
cos_x = PatternTerm("cos", [x])
sin_x = PatternTerm("sin", [x])

def reverse(r: Rule) -> Rule:
    return Rule(r.right, r.left)

divide_self_equal_one = Rule(
    PatternTerm("/", [x, x]),
    one
)
multiply_divide_equal_divide_multiply = Rule(
    PatternTerm("/", [PatternTerm("*", [x, w]), PatternTerm("*", [y, z])]),
    PatternTerm("*", [PatternTerm("/", [x, y]), PatternTerm("/", [w, z])])
)
sin2_cos2_equal_one = Rule(
    PatternTerm("+", [
        PatternTerm("*", [PatternTerm("sin", [x]), PatternTerm("sin", [x])]),
        PatternTerm("*", [PatternTerm("cos", [x]), PatternTerm("cos", [x])])
    ]),
    one
)
hallucinate_one_add_sin = Rule(
    PatternTerm("/", [PatternTerm("-", [one, sin_x]), cos_x]),
    PatternTerm("*", [
        PatternTerm("/", [PatternTerm("-", [one, sin_x]), cos_x]),
        PatternTerm("/", [PatternTerm("+", [one, sin_x]), PatternTerm("+", [one, sin_x])])
    ])
)
hallucinate_cos = Rule(
    PatternTerm("/", [cos_x, PatternTerm("+", [one, sin_x])]),
    PatternTerm("*", [
        PatternTerm("/", [cos_x, PatternTerm("+", [one, sin_x])]),
        PatternTerm("/", [cos_x, cos_x])
    ])
)

rules = [
    divide_self_equal_one,
    multiply_divide_equal_divide_multiply, reverse(multiply_divide_equal_divide_multiply),
    sin2_cos2_equal_one,
    hallucinate_one_add_sin,
    hallucinate_cos
]
