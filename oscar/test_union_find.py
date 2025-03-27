from union_find import UnionFind

def test_union_find():
    n = 10
    u = UnionFind()

    for _ in range(n):
        u.add()

    assert(u.parents == list(range(n)))

    u.union(0, 1)
    u.union(0, 2)
    u.union(0, 3)

    u.union(6, 7)
    u.union(6, 8)
    u.union(6, 9)

    # compress all the paths
    for i in range(n):
        u.find(i)

    # indices:  0  1  2  3  4  5, 6, 7, 8, 9
    expected = [0, 0, 0, 0, 4, 5, 6, 6, 6, 6]
    assert(u.parents == expected)
