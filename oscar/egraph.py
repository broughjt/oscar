from __future__ import annotations
from dataclasses import dataclass
from functools import reduce
from itertools import chain, groupby
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
    operator: str
    operands: list[PatternTerm | PatternVariable]
    
Pattern = Union[PatternTerm, PatternVariable]

Substitution = Mapping[PatternVariable, EClassId]

@dataclass(frozen=True)
class Rule:
    left: Pattern
    right: Pattern

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
        # 1.
        # while self.pending:
        #     # TODO:
        #     # pending = self.pending
        #     # Remove duplicate consecutive entries
        #     # https://stackoverflow.com/questions/5738901/removing-elements-that-have-consecutive-duplicates#5738933
        #     # pending = [a for a, _ in groupby(self.pending)]
        #     pending = self.
        #     self.pending = list()
        #     for a in pending:
        #         self.repair(self.find(a))

        # 2.
        # while len(self.pending) > 0:
        #     self.repair(self.find(self.pending.pop()))

        # 3.
        while len(self.pending) > 0:
            pending = { self.find(a) for a in self.pending }
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
            try:
                self.hash_cons.pop(n)
            except:
                pass
            self.hash_cons[self.canonicalize(n)] = self.find(b)

        # Upward merge
        parents = dict()
        did_union = False
        for (n, b) in e.parents:
            n = self.canonicalize(n)
            if c := parents.get(n):
                self.union(b, c)
                did_union = True
            parents[n] = self.find(b)
        self.classes[a].parents = list(parents.items())

    # Efficient E-matching for SMT Solvers Figure 1 p. 186
    #
    # De Moura and Bjorner (Section 2.1, p. 185) write "the set of
    # relevant substitutions for a pattern $p$ can be obtained by
    # taking $\bigcup_{t \in E} \match(p, t, \emptyset)$," but it
    # needs to be the set containing an empty subsitution or the
    # handler for variables will never bind anything in the first
    # place. If we initially pass the set containing an empty
    # subsitution then the handler bind the first variable and that
    # gets the whole thing going. If you try to add a special case for
    # an empty subsitution set, you will inadvertently bind variables
    # to an already failed match. Doing it this way preserves the
    # property that if an earlier sibling node failed a pattern,
    # latter sibling nodes will respect this decision because they
    # will never see that subsitution. Poorly written, I'm having a
    # hard time saying it concisely.
    def ematch_at(self, p: Pattern, a: EClassId, S: set[Substitution]) -> set[Substitution]:
        """
        Find nodes in `a` which match the pattern `p`, returning
        for each match a substitution which maps pattern variables to
        e-class ids.
        """
        a = self.find(a)
        match p:
            case PatternVariable(x):
                return { s | pmap({x: a}) for s in S if x not in s} \
                    | { s for s in S if x in s and self.find(s[x]) == a }
            case PatternTerm(f, ps):
                return set(chain.from_iterable((
                    # We use a fold here because matching later
                    # arguments depends on the subsitutions made for
                    # earlier arguments.

                    # Curse you Perry the Platypus/Guido van Rossum!
                    # Why no pattern matching for lambdas?
                    # curses = (pattern, e-class) = (p, b)
                    reduce(lambda S, curses: self.ematch_at(curses[0], curses[1], S), zip(ps, n.operands), S)
                    for n in self.classes[a].nodes
                    if f == n.operator and len(ps) == len(n.operands)
                )))

    # De Moura and Bjorner (section 1.2, p. 185) write: "The set of
    # relevant substitutions for a pattern p can be obtained by taking
    # $\bigcup_{t \in E} match(p, t, \emptyset)$."  But shouldn't it
    # be $match(p, t, \left{ \emptyset \right})$? Otherwise I don't
    # see any to ever match a variable, as the rule for pattern
    # variables returns set builders over $S$. Doing it this way seems
    # to work.
    def ematch(self, p: Pattern) -> list[tuple[Substitution, EClassId]]:
        """
        Find nodes in the e-graph which match the pattern `p`. For
        each match, return a substitution which maps pattern variables
        to e-class ids and the e-class id of the node which matched.
        """
        return list(chain.from_iterable((
            ((s, a) for s in self.ematch_at(p, a, {pmap()}))
            for a in self.classes.keys()
        )))

    # I think this is right? If the right-hand side of the
    # pattern is just a variable, we shouldn't add any new
    # nodes, just union the e-class with one of it's
    # matched children. Similarly, if the right-hand side
    # is deeply nested and contains terms which aren't
    # even in the e-graph yet, we have to add them before
    # we can we refer to the as nodes in a particular
    # e-class.
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
        return sum((len(e.nodes) for e in self.classes.values()))

    def run(self, rs: list[Rule], l: int = 1_000_000) -> int:
        """
        This week on Yankee and The Brave
        """
        # The e-graph is "saturated" when we reach a fixed point, in
        # the sense that running the rules doesn't add any new nodes.
        # Since we never remove anything, it is sufficient to check
        # the total node count.

        for i in range(1, l+1):
            k = self.count_nodes()
            ms = list(chain.from_iterable((
                ((r, s, a) for (s, a) in self.ematch(r.left))
                for r in rs
            )))
                    
            for (r, s, a) in ms:
                b = self.substitute_add(r.right, s)
                # match substitute(r.right, s):
                #     case EClassId() as _b:
                #         b = _b
                #     case ENode() as n:
                #         b = self.add(n)
                self.union(a, b)
            self.rebuild()

            if k == self.count_nodes():
                return i

        return l
