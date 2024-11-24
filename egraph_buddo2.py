from dataclasses import dataclass

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

    def makeset(self):
        x = eclass_id_to_symbol(len(self.eclasses))
        self.eclasses.append(x)
        return x

    def make(self, t : ENode) -> EClass:
        t1 = self.hash_cons.get(t)
        if t1 == None:
            v = self.makeset()
            self.hash_cons[t] = v
            return v
        else:
            return t1

    def rebuild(self):
        # simple naive dumb rebuild step. Could be optimized significantly
        while True:
            #rebuild "union find", buchberhe
            self.equations = list(sp.groebner(self.equations, *self.eclasses))

            hash_cons1 = {}
            for k,v in self.hash_cons.items():
                (f,*args) = k
                args = map(self.find,args) # normalize argument eclasses
                enode = (f,*args)
                eclass = self.hash_cons.get(enode)
                if eclass != None:
                    self.union(v,eclass)
                hash_cons1[enode] = self.find(v)
            if self.hash_cons == hash_cons1: # reached fixed point
                return
            self.hash_cons = hash_cons1   

    def add_term(self, t):
        if isinstance(t, sp.Expr): # allow partial terms that contain eclasses
            return t
        f, *args = t
        args = map(self.add_term,args)
        return self.make_enode((f,*args))

    def check_term(self, t):
        if isinstance(t, sp.Expr): # allow partial terms that contain eclasses
            return t
        f, *args = t
        map(self.check_term,args)
        return (f,*args)

    def make_enode(self, enode):
        eclass = self.hash_cons.get(enode)
        if eclass == None:
            eclass = self.makeset() 
            self.hash_cons[enode] = eclass
        return eclass
    
def eclass_id_to_symbol(n):
    return sp.symbols(f"e{n}")

def eclass_id_from_symbol(s):
    return int(s.name[1:])
