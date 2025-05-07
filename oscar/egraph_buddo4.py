from __future__ import annotations
from dataclasses import dataclass
from functools import reduce
from itertools import chain
from pyrsistent import pmap
from sympy import Expr, Integer, Symbol, symbols, reduced, groebner
from typing import Mapping

EClassId = Symbol

@dataclass(frozen=True)
class TermNode:
    operator: str
    operands: tuple[Term]

Term = str | int | TermNode

@dataclass(frozen=True)
class ENode:
    operator: str
    operands: tuple[EClassId]

@dataclass
class EGraph:
    basis: list[Expr]
    ids: list[EClassId]
    hash_cons: dict[ENode, EClassId]
    classes: dict[Expr, list[ENode]]

@dataclass(frozen=True)
class PatternVariable:
    identifier: str

@dataclass(frozen=True)
class PatternTerm:
    operator: str
    operands: list[PatternTerm | PatternVariable]
    
Pattern = PatternTerm | PatternVariable

Substitution = Mapping[PatternVariable, EClassId]

@dataclass(frozen=True)
class Rule:
    left: Pattern
    right: Pattern

@dataclass
class EGraph:
    basis: list[Expr]
    ids: list[EClassId]
    hash_cons: dict[ENode, EClassId]
    classes: dict[EClassId, list[ENode]]

    def __init__(self):
        self.basis = list()
        self.ids = list()
        self.hash_cons = dict()
        self.classes = dict()

    def find(self, a: EClassId) -> EClassId:
        qs, r = reduced(a, self.basis, *self.ids)
        return r

    def canonicalize(self, n: ENode) -> ENode:
        return ENode(n.operator, tuple((self.find(a) for a in n.operands)))

    def add(self, n: ENode) -> EClassId:
        n = self.canonicalize(n)
        if n in self.hash_cons:
            return self.find(self.hash_cons[n])
        else:
            k = len(self.ids)
            a = symbols(f"e{k}")
            self.ids.append(a)
            self.hash_cons[n] = a

            match n:
                case ENode("+", [b, c]):
                    d = b + c
                case ENode("-", [b]):
                    d = -b
                case ENode("-", [b, c]):
                    d = b - c
                case ENode("*", [b, c]):
                    d = b * c
                case ENode(int() as b, []):
                    d = Integer(b)
                case _:
                    d = None
                                
            if d is not None:
                a = self.union(a, d)

            return a

    def add_term(self, t: Term) -> EClassId:
        match t:
            case int():
                return self.add(ENode(t, tuple()))
            case str():
                return self.add(ENode(t, tuple()))
            case TermNode(f, us):
                return self.add(ENode(f, tuple((
                    self.add_term(u) for u in us
                ))))

    def union(self, a: EClassId, b: EClassId) -> EClassId:
        c = self._union(a, b)
        self.rebuild()
        return self.find(c)

    def _union(self, a: EClassId, b: EClassId) -> EClassId:
        a = self.find(a)
        b = self.find(b)
        if a == b:
            return a
        else:
            self.basis.append(a - b)
            return self.find(a)

    def rebuild(self):
        while True:
            self.basis = list(groebner(self.basis, *self.ids))
        
            hash_cons = dict()
            for n, a in list(self.hash_cons.items()):
                n = self.canonicalize(n)
                b = self.hash_cons.get(n)

                if b is not None:
                    c = self._union(a, b)
                else:
                    c = self.find(a)
                hash_cons[n] = c
            if self.hash_cons == hash_cons:
                break
            else:
                self.hash_cons = hash_cons
                    
        classes = dict()
        for n, a in self.hash_cons.items():
            if a in classes:
                classes[a].append(n)
            else:
                classes[a] = [n]
        self.classes = classes

        # enodes in the hashcons should be canonical
        classes2 = set(classes)
        for n in hash_cons.keys():
            assert set(n.operands) <= classes2, f"{set(n.operands)}\n{classes2}"

    def count_nodes(self) -> int:
        return sum((len(ns) for ns in self.classes.values()))

    # See `ematch_at` in the non-frankenstein-monster e-graph
    def ematch_at(self, p: Pattern, a: EClassId, S: set[Substitution]) -> set[Substitution]:
        a = self.find(a)
        match p:
            case PatternVariable(x):
                return { s | pmap({x: a}) for s in S if x not in s} \
                    | { s for s in S if x in s and self.find(s[x]) == a }
            case PatternTerm(f, ps):
                return set(chain.from_iterable((
                    reduce(lambda S, curses: self.ematch_at(curses[0], curses[1], S), zip(ps, n.operands), S)
                    for n in self.classes[a]
                    if f == n.operator and len(ps) == len(n.operands)
                )))

    def ematch(self, p: Pattern) -> list[tuple[Substitution, EClassId]]:
        return list(chain.from_iterable((
            ((s, a) for s in self.ematch_at(p, a, {pmap()}))
            for a in self.classes.keys()
        )))

    def substitute_add(self, p: Pattern, s: Substitution) -> EClassId:
        match p:
            case PatternVariable(x):
                return s[x]
            case PatternTerm(f, ps):
                return self.add(ENode(f, tuple((self.substitute_add(p, s) for p in ps))))
