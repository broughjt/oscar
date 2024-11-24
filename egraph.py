# https://www.philipzucker.com/linear_grobner_egraph/

from dataclasses import dataclass

import sympy as sp

EClass = sp.Symbol
ENode = tuple[str, ...]

@dataclass
class EGraph:
    equations: list[sp.Expr]
    hash_cons: dict[ENode, EClass]
    eclasses: list[EClass]

    def __init__(self):
        self.equations = list()
        self.hash_cons = dict()
        self.eclasses = list()

    # Find canonicalizes an eclass?
    def find(self, x: EClass) -> EClass:
        # TODO: Appropriate names?
        _, x1 = sp.reduced(x, self.equations, self.eclasses)
        return x

    def union(self, x: EClass, y: EClass) -> EClass:
        x = self.find(x)
        y = self.find(y)
        if x != y:
            self.equations.append(x - y)

    # Original name is makeset
    # TODO: What is it doing?
    # Make new eclass?
    def append_eclass(self):
        x = eclass_to_symbol(len(self.eclasses))
        self.eclasses.append(x)
        return x

    # TODO:
    # def append_enode(self, enode: ENode) -> ENode:
    #     eclass = self.hash_cons.get(enode)
    #     if eclass := self.hash_cons.get(enode):
    #         return eclass
    #     else:
    #         eclass = self.append_eclass()
    #         self.hash_cons[enode] = eclass
    #         return eclass

    def rebuild(self):
        while True:
            self.equations = list(sp.groebner(self.equations, *self.eclasses))

            hash_cons1 = dict()
            for enode, eclass in self.hash_cons.items():
                (operator, *operands) = enode
                operands1 = map(self.find, operands)
                enode1 = (operator, *operands1)
                eclass1 = self.hash_cons.get(enode1)
                if eclass1 is not None:
                    self.union(eclass, eclass1)
                hash_cons1[enode1] = self.find(eclass)
            if self.hash_cons == hash_cons1:
                return
            self.hash_cons = hash_cons1

    def append_term(self, term):
        if isinstance(term, sp.Expr):
            return term
        operator, *operands = term
        operands1 = map(self.append_term, operands)
        return self.append_enode((operator, *operands1))

    def check_term(self, term):
        if isinstance(term, sp.Expr):
            return term
        operator, *operands = term
        map(self.check_term, operands)
        return (operator, *operands)

    def append_enode(self, enode):
        eclass = self.hash_cons.get(enode)
        if eclass is None:
            eclass = self.append_eclass()
            self.hash_cons[enode] = eclass
        return eclass

def eclass_to_symbol(n):
    return sp.symbols("e" + str(n))

def eclass_from_symbol(eclass):
    return int(eclass.name[1:])
