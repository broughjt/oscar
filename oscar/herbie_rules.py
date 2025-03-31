from egraph import *

x = PatternVariable("x")
y = PatternVariable("y")
z = PatternVariable("z")
w = PatternVariable("w")
zero = PatternTerm("0", tuple())
one = PatternTerm("1", tuple())

def reverse(r: Rule) -> Rule:
    return Rule(r.right, r.left)

add_commutative = Rule(
    PatternTerm("+", [x, y]),
    PatternTerm("+", [y, x])
)
add_associative = Rule(
    PatternTerm("+", [PatternTerm("+", [x, y]), z]),
    PatternTerm("+", [x, PatternTerm("+", [y, z])])
)
add_identity_left = Rule(
    PatternTerm("+", [zero, x]),
    x
)
add_identity_right = Rule(
    PatternTerm("+", [x, zero]),
    x
)
add_inverse_left = Rule(
    PatternTerm("+", [PatternTerm("negate", [x]), x]),
    zero
)
add_inverse_right = Rule(
    PatternTerm("+", [x, PatternTerm("negate", [x])]),
    zero
)
negate_involutive = Rule(
    PatternTerm("negate", [PatternTerm("negate", [x])]),
    x
)
subtract_definition = Rule(
    PatternTerm("+", [x, PatternTerm("negate", [y])]),
    PatternTerm("-", [x, y])
)

multiply_commutative = Rule(
    PatternTerm("*", [x, y]),
    PatternTerm("*", [y, x])
)
multiply_associative = Rule(
    PatternTerm("*", [PatternTerm("*", [x, y]), z]),
    PatternTerm("*", [x, PatternTerm("*", [y, z])])
)
multiply_identity_left = Rule(
    PatternTerm("*", [one, x]),
    x
)
multiply_identity_right = Rule(
    PatternTerm("*", [x, one]),
    x
)
multiply_inverse_left = Rule(
    PatternTerm("*", [PatternTerm("^-1", [x]), x]),
    one
)
multiply_inverse_right = Rule(
    PatternTerm("x", [x, PatternTerm("^-1", [x])]),
    one
)
multiply_distributes_over_add_left = Rule(
    PatternTerm("*", [x, PatternTerm("+", [y, z])]),
    PatternTerm("+", [PatternTerm("*", [x, y]), PatternTerm("*", [x, z])])
)
multiply_distributes_over_add_right = Rule(
    PatternTerm("*", [PatternTerm("+", [x, y]), z]),
    PatternTerm("+", [PatternTerm("*", [x, z]), PatternTerm("*", [y, z])])
)
multiply_annihilator_left = Rule(
    PatternTerm("*", [zero, x]),
    zero
)
multiply_annihilator_right = Rule(
    PatternTerm("*", [x, zero]),
    zero
)
reciprocal_involutive = Rule(
    PatternTerm("^-1", [PatternTerm("^-1", [x])]),
    x
)
divide_definition = Rule(
    PatternTerm("*", [x, PatternTerm("^-1", [y])]),
    PatternTerm("/", [x, y])
)
divide_self_equal_one = Rule(
    PatternTerm("/", [x, x]),
    one
)
multiply_divide_equal_divide_multiply = Rule(
    PatternTerm("/", [PatternTerm("*", [x, w]), PatternTerm("*", [y, z])]),
    PatternTerm("*", [PatternTerm("/", [x, y]), PatternTerm("/", [w, z])])
)

hallucinate_one_add_sin = Rule(
    x,
    PatternTerm("*", [x, PatternTerm("/", [
        PatternTerm("+", [one, PatternTerm("sin", [x])]),
        PatternTerm("+", [one, PatternTerm("sin", [x])])
    ])])
)
sin2_cos2_equal_one = Rule(
    PatternTerm("+", [
        PatternTerm("*", [PatternTerm("sin", [x]), PatternTerm("sin", [x])]),
        PatternTerm("*", [PatternTerm("cos", [x]), PatternTerm("cos", [x])])
    ]),
    one
)
one_minus_sin2_equal_cos2 = Rule(
    PatternTerm("-", [one, PatternTerm("*", [PatternTerm("sin", [x]), PatternTerm("sin", [x])])]),
    PatternTerm("*", [PatternTerm("cos", [x]), PatternTerm("cos", [x])])
)

rules = [
    add_commutative,
    add_associative, reverse(add_associative),
    add_identity_left, reverse(add_identity_left),
    add_identity_right, reverse(add_identity_right),
    add_inverse_left,
    add_inverse_right,
    negate_involutive, reverse(negate_involutive),
    subtract_definition, reverse(subtract_definition),

    multiply_commutative,
    multiply_associative, reverse(multiply_associative),
    multiply_identity_left, reverse(multiply_identity_left),
    multiply_identity_right, reverse(multiply_identity_right),
    multiply_inverse_left,
    multiply_inverse_right,
    multiply_distributes_over_add_left, reverse(multiply_distributes_over_add_left),
    multiply_distributes_over_add_right, reverse(multiply_distributes_over_add_right),
    # multiply_annihilator_left,
    # multiply_annihilator_right,
    reciprocal_involutive, reverse(reciprocal_involutive),
    divide_definition, reverse(divide_definition),
    divide_self_equal_one,
    multiply_divide_equal_divide_multiply, reverse(multiply_divide_equal_divide_multiply),

    hallucinate_one_add_sin,
    sin2_cos2_equal_one,
    one_minus_sin2_equal_cos2
]
