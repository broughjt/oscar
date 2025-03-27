from __future__ import annotations
from dataclasses import dataclass
from functools import reduce
from itertools import chain
from pprint import pprint
from pyrsistent import pmap
from typing import Union, Mapping
from union_find import UnionFind

# From https://www.philipzucker.com/egraph-1/:
#
# The E-graph maintains:
#
# - a map from hash-consed terms to class ids
# - a map from class-ids to equivalence classes
# - a unionfind data structure on class ids
#
# Each equivalence class needs to maintain:
#
# - an array of terms in the class
# - an array of possible parent terms for efficiently propagating congruences

EClassId = int

@dataclass(frozen=True)
class Term:
    operator: str
    # Tuples are hashable, lists are not
    operands: tuple[Term]

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
    operand: str
    operator: list[PatternTerm | PatternVariable]
    
Pattern = Union[PatternTerm, PatternVariable]

Substitution = Mapping[PatternVariable, EClassId]

@dataclass
class Rule:
    left: Pattern
    right: Pattern

def substitute(p: Pattern, s: Substitution) -> ENode | EClassId:
    match p:
        case PatternVariable(x):
            return s[x]
        case PatternTerm(f, ps):
            return ENode(f, tuple((substitute(p, s) for p in ps)))

class EGraph:
    def __init__(self):
        self.union_find = UnionFind()
        # Maps ENodes to e-class ids
        self.hash_cons = dict()
        # Maps e-class ids to e-classes
        self.classes = dict()
        # List of e-class ids which need to be upward merged
        self.pending = list()

    def find(self, a: EClassId) -> EClassId:
        """
        Find the canonical e-class id for a given e-class.
        """
        return self.union_find.find(a)

    def canonicalize(self, n: ENode) -> ENode:
        """
        Return a version `n` where each of its children are
        canonical e-class ids.
        """
        return ENode(n.operator, tuple((self.find(a) for a in n.operands)))

    def add(self, n: ENode) -> EClassId:
        """
        Add a node to the egraph.

        Use the hashcons to check if this node already
        exists. Otherwise make a new singleton e-class.
        """
        n = self.canonicalize(n)
        # Note, can't do walrus `a := self.hash_cons.get(n)` here
        # because 0 is a possible e-class id but that's a falsey value
        # in Python. This was a bug for me earlier.
        if n in self.hash_cons:
            return self.find(self.hash_cons[n])
        else:
            # Make a new singleton e-class
            a = self.union_find.add()
            e = EClass(nodes=[n], parents=list())
            # Add node `n` to the parent lists of its children.
            #
            # We already canonicalized the children, so we don't need
            # to do it again here.
            for b in n.operands:
                self.classes[b].parents.append((n, a))
            self.classes[a] = e
            self.hash_cons[n] = a
            return a

    def add_term(self, t: Term) -> EClassId:
        """
        Helper method for adding a whole term to the e-graph.
        """
        return self.add(ENode(
            t.operator,
            tuple((self.add_term(s) for s in t.operands))
        ))

    def union(self, a: EClassId, b: EClassId) -> bool:
        """
        Union two e-classes.

        If the two e-classes aren't already the same, union the two
        ids in the union find, merge the node and parent lists of the
        two e-classes, and add the e-class to the work list since there
        might now be parents which should be congruent but aren't yet.
        """
        a = self.find(a)
        b = self.find(b)
        if a == b:
            # Don't do extra work
            return False
        else:
            # The items contained second e-class get moved into first e-class,
            # so the second should be smaller to reduce work
            if len(self.classes[a].parents) < len(self.classes[b].parents):
                a, b = b, a

            self.union_find.union(a, b)
               
            # Newly unioned e-class now needs upward merging.
            #
            # Note: Egg adds the entire parent list here, but the egg
            # paper does not. This seems to work right now.
            self.pending.append(a)
               
            # Set M[a] := M[a] \cup M[b]
            e = self.classes.pop(b)
            self.classes[a].nodes.extend(e.nodes)
            self.classes[a].parents.extend((p, self.find(b)) for p, b in e.parents)

            return True

    def rebuild(self):
        """
        Restore the hashcons and congruence invariants.
        """
        while self.pending:
            pending = self.pending
            self.pending = list()
            for a in pending:
                self.repair(self.find(a))

    def repair(self, a: EClassId):
        """
        Not sure I've got rebuilding down solid yet.

        It is the caller's responsibility to pass a canonical e-class id.
        """
        e = self.classes[a]

        # Fix the hash-cons
        for (n, b) in e.parents:
            self.hash_cons.pop(n)
            self.hash_cons[self.canonicalize(n)] = self.find(b)

        # Upward merge
        parents = dict()
        for (n, b) in e.parents:
            n = self.canonicalize(n)
            if c := parents.get(n):
                self.union(b, c)
            parents[n] = self.find(b)
        self.classes[a].parents = list(parents.items())

    # Relational E-matching Zhang et al. Figure 3
    #
    # God bless the UW crew for making that figure! Excellent
    # two-liner describing the naive e-matching algorithm from the
    # Simplify paper which I seriously could not find. The thing
    # is like 150 pages long and has no index or table of contents.
    def ematch_at(self, p: Pattern, a: EClassId, S: set[Substitution]) -> set[Substitution]:
        """
        Find nodes in `a` which match the pattern `p`. For each
        match, return a substitution which maps pattern variables to
        e-class ids.
        """
        a = self.find(a)
        match p:
            case PatternVariable(x):
                if S:
                    # Keep the current substitution if we've already bound
                    # to this e-class, otherwise add this binding to the
                    # substitution

                    # Curse you Perry the Platypus/Guido van Rossum
                    # I want to call map on the option but that's not a thing
                    return { (s if (b := s.get(x) and self.find(b)) == a else (pmap({x: a}) | s)) for s in S }
                else:
                    # If the set of subsitutions is currently empty,
                    # new variable binding happens here
                    return { pmap({x: a}) }
            case PatternTerm(f, ps):
                return set(chain.from_iterable((
                    # We're reducing here so that, for example, if the
                    # pattern is `f(x, g(x, y))`, that we know what
                    # `x` is by the time we reach `g`.

                    # More curses: why no pattern matching for lambdas?
                    # curses = (pattern, e-class) = (p, b)
                    reduce(lambda S, curses: self.ematch_at(curses[0], curses[1], S), zip(ps, n.operands), S)
                    for n in self.classes[a].nodes
                    if f == n.operator
                )))

    def ematch(self, p: Pattern) -> list[tuple[Substitution, EClassId]]:
        """
        Find nodes in the e-graph which match the pattern `p`. For
        each match, return a substitution which maps pattern variables
        to e-class ids and the e-class id of the node which matched.
        """
        return list(chain.from_iterable((
            ((s, a) for s in self.ematch_at(p, a, set()))
            for a in self.classes.keys()
        )))

    def count_nodes(self) -> int:
        """
        Count the total number of nodes in the e-graph.
        """
        return sum((len(e.nodes) for e in self.classes.values()))

    def run(self, rs: list[Rule], l: int = 1_000_000) -> int:
        """
        This week on Yankee and The Brave
        """
        # When is the e-graph saturated? When we hit a fixed point, in
        # the sense that running the rules doesn't add any new
        # nodes. Since we never remove anything, it is sufficient to
        # check the total node count.

        for i in range(1, l+1):
            k = self.count_nodes()
            ms = list(chain.from_iterable((
                ((r, s, a) for (s, a) in self.ematch(r.left))
                for r in rs
            )))
                    
            for (r, s, a) in ms:
                # I think this is right? If the right hand side of the
                # rule is just a variable, that corresponds to an
                # e-class id, so there's no new node to add in that
                # case, we should just union the child e-class with
                # the e-class of the parent node.
                match substitute(r.right, s):
                    case EClassId() as _b:
                        b = _b
                    case ENode() as n:
                        b = self.add(n)
                self.union(a, b)
            self.rebuild()

            if k == self.count_nodes():
                return i

        return l
