from __future__ import annotations
from dataclasses import dataclass
from sympy import Expr, Symbol, Integer, reduced, symbols, groebner
from typing import Mapping
from itertools import chain

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
class EClass:
    nodes: list[ENode]
    parents: list[tuple[ENode, EClassId]]

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
    classes: dict[EClassId, EClass]
    pending: list[tuple[EClassId, EClassId]]

    def __init__(self):
        self.basis = list()
        self.hash_cons = dict()
        self.classes = dict()
        self.ids = list()
        self.pending = list()

    def find(self, a: EClassId) -> EClassId:
        qs, r = reduced(a, self.basis, *self.ids)
        return r

    def canonicalize(self, n: ENode) -> ENode:
        return ENode(n.operator, tuple((self.find(a) for a in n.operands)))

    def add(self, n: ENode) -> EClassId:
        print(f"Adding {n.operator, n.operands}", self.ids, list(self.classes.keys()), self.basis)
        n = self.canonicalize(n)
        if n in self.hash_cons:
            print("Already got it")
            return self.find(self.hash_cons[n])
        else:
            # Okay so the e-class ids in `ids` are the generators of
            # the polynomail ring we're working in. The problem is
            # that if we're wanting to add an integer constant to our
            # e-graph, and we make a new generator and union it with
            # the integer 1, our ideal now contains 1, which means its
            # the entire ring, and quotienting by it will yield the
            # trivial ring. So I'm special casing integers for
            # now. There might be a more general way to handle all
            # ring ops, but I haven't thought of it yet
            match n:
                case ENode(int() as b, []):
                    # This wasn't in the hash-cons, so we haven't added
                    # this integer yet.
                    # 
                    # Crucially, *do not* add this e-class as a generator
                    #
                    # Are integers always their own canonical form?
                    # Probably, but maybe not, so I'm going to be safe
                    # and not assume this for now
                    e = EClass(nodes=[n], parents=list())
                    a = self.find(b)
                    self.classes[a] = e
                    self.hash_cons[n] = a
                case _:
                    # Normal case, new singleton e-class will become a generator
                    k = len(self.ids)
                    a = symbols(f"e{k}")
                    self.ids.append(a)
                    
                    e = EClass(nodes=[n], parents=list())
                    for b in n.operands:
                        self.classes[b].parents.append((n, a))
                    self.classes[a] = e
                    self.hash_cons[n] = a
                        
                    # Okay, now some weird shit
                    match n:
                        case ENode("+", [b, c]):
                            d = b + c
                        case ENode("-", [b]):
                            d = -b
                        case ENode("-", [b, c]):
                            d = b - c
                        case ENode("*", [b, c]):
                            d = b * c
                        case _:
                            d = None
                                
                    if d is not None:
                        a = self.union(a, d, b_fake=True)

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

    def union(self, a: EClassId, b: EClassId | Expr, b_fake=False) -> EClassId:
        a = self.find(a)
        b = b if b_fake else self.find(b)
        if a == b:
            return a
        else:
            u = self.classes.pop(a)
            v = self.classes.pop(b, EClass(list(), list())) if b_fake else self.classes.pop(b)

            c = self._union(a, b)

            self.pending.append(c)

            self.classes[c] = EClass(
                u.nodes + v.nodes,
                [(n, self.find(d)) for n, d in chain(u.parents, v.parents)]
            )

            return c

    def _union(self, a: EClassId, b: EClassId | Expr) -> EClassId:
        self.basis.append(a - b)
        self.basis = list(groebner(self.basis))
        assert(self.find(a) == self.find(b))
        return self.find(a)

    # def rebuild(self):
    #     while len(self.pending) > 0:

