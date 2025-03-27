# Copied from
# https://github.com/egraphs-good/egg/blob/main/src/unionfind.rs

class UnionFind:
    def __init__(self):
        self.parents = list()

    def add(self) -> int:
        l = len(self.parents)
        self.parents.append(l)
        return l

    def find(self, x: int) -> int:
        """
        Find the canonical representative of the equivalence class
        which contains `x`.

        I think this is path-splitting, which replaces every parent
        pointer on the path to the root with its parent (grandparent
        of current).

        """
        assert x < len(self.parents)
        while x != self.parents[x]:
            grandparent = self.parents[self.parents[x]]
            self.parents[x] = grandparent
            x = grandparent
        return x

    def union(self, x: int, y: int) -> int:
        """
        Union two equivalence classes.
        """
        self.parents[y] = x
        return x

        
