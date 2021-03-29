from itertools import product, combinations
from math import cos, sin, pi, dist

v = []
radius = 10
n = 50
for i in range(n):
    x = radius * cos(pi / n * (1 + 2 * i))
    y = radius * sin(pi / n * (1 + 2 * i))
    v.append((x, y))

tri = []
for i in combinations(list(range(n)), 3):
    for j in range(3):
        m = i[j]
        a, b = filter(lambda x: x != m, i)
        if abs(dist(v[m], v[a]) - dist(v[m], v[b])) < 10 ** -10:
            tri.append((m, a, b))

print(len(tri))
count = 0
for i in tri:
    if 0 in i and 2 in i:
        count += 1
print(count)
