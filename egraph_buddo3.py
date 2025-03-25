from dataclasses import dataclass

import itertools
import sympy as sp

EClass = sp.Symbol
ENode = tuple[str,...]

@dataclass
class EGraph:
    equations: list[sp.Expr]
    hash_cons: dict[ENode, EClass]
    eclasses: list[EClass]
    
    def __init__(self):
        self.equations = list()
        self.hash_cons = dict()
        self.eclasses = list()

    def find(self, x : EClass) -> EClass:
        return sp.reduced(x, self.equations, self.eclasses)[1]

    def union(self, x : EClass,y : EClass) -> EClass:
        x = self.find(x)
        y = self.find(y)
        if x != y:
            self.equations.append(x - y)

    def append_eclass(self):
        x = eclass_id_to_symbol(len(self.eclasses))
        self.eclasses.append(x)
        return x

    def append_term(self, term):
        if isinstance(term, sp.Expr):
            return term
        operator, *operands = term
        operands1 = map(self.append_term, operands)
        return self.append_enode((operator, *operands1))

    def append_enode(self, enode):
        eclass = self.hash_cons.get(enode)
        if eclass is None:
            eclass = self.append_eclass() 
            self.hash_cons[enode] = eclass
        return eclass

    def rebuild(self):
        while True:
            self.equations = list(sp.groebner(self.equations, *self.eclasses))

            hash_cons1 = {}
            for enode, eclass in self.hash_cons.items():
                (operator, *operands) = enode
                operands1 = map(self.find, operands)
                enode1 = (operator, *operands1)
                eclass1 = self.hash_cons.get(enode1)
                if eclass1 is not None:
                    self.union(eclass, eclass1)
                hash_cons1[enode1] = self.find(eclass)
            if self.hash_cons == hash_cons1: # reached fixed point
                return
            self.hash_cons = hash_cons1   

    def rewrite(self, arguments_length, rule):
        for eclasses in itertools.product(self.eclasses, repeat=arguments_length):
            l, r = rule(*eclasses)
            l = self.append_term(l)
            r = self.append_term(r)
            self.union(l, r)

def eclass_id_to_symbol(n):
    return sp.symbols(f"e{n}")

def eclass_id_from_symbol(s):
    return int(s.name[1:])
