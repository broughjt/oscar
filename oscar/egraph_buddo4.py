from __future__ import annotations
from dataclasses import dataclass
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
            for n, a in self.hash_cons.items():
                n = self.canonicalize(n)
                b = self.hash_cons.get(n)

                if b is not None:
                    c = self.union(a, b)
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

    def count_nodes(self) -> int:
        return sum((len(ns) for ns in self.classes.values()))
