from __future__ import annotations
from dataclasses import dataclass
from functools import reduce
from itertools import chain
from pprint import pprint
from pyrsistent import pmap
from sympy import Expr, Symbol, Integer, reduced, symbols, groebner
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
    classes: dict[Expr, list[ENode]]

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
                    # e = EClass(nodes=[n], parents=list())
                    a = b
                    self.hash_cons[n] = a
                case _:
                    # Normal case, new singleton e-class will become a generator
                    k = len(self.ids)
                    a = symbols(f"e{k}")
                    self.ids.append(a)
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

    def _union(self, a: EClassId, b: EClassId) -> EClassId:
        a = self.find(a)
        b = self.find(b)
        if a == b:
            return a
        else:
            self.basis.append(a - b)
            self.basis = list(groebner(self.basis, *self.ids))
            assert(self.find(a) == self.find(b))
            return self.find(a)

    def union(self, a: EClassId, b: EClassId) -> EClassId:
        c = self._union(a, b)
        self.rebuild()
        return self.find(c)

    def rebuild(self):
        i = 0
        while True:
            self.basis = list(groebner(self.basis, *self.ids))
        
            hash_cons = dict()
            for n, a in self.hash_cons.items():
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
                i += 1
                self.hash_cons = hash_cons
                    
        # Realize the classes explicitly
        classes = dict()
        for n, a in self.hash_cons.items():
            if a in classes:
                classes[a].append(n)
            else:
                classes[a] = [n]
        self.classes = classes

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

    def count_nodes(self) -> int:
        """
        Count the total number of nodes in the e-graph.
        """
        return sum((len(e) for e in self.classes.values()))
    
    def run(self, rs: list[Rule], l: int = 1_000_000) -> int:
        for i in range(1, l+1):
            k = self.count_nodes()
            ms = list(chain.from_iterable((
                ((r, s, a) for (s, a) in self.ematch(r.left))
                for r in rs
            )))
            print(f"----------- Iteration {i} ---------------")
            # for a, ns in self.classes.items():
            #     print(a, ms)
            # pprint(ms)
                    
            for (r, s, a) in ms:
                b = self.substitute_add(r.right, s)
                self.union(a, b)
            # self.rebuild()

            if k == self.count_nodes():
                return i

        return l
