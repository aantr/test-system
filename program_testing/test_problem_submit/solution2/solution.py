# Динамическое программирование - это когда у нас
# есть одна большая задача, которую непонятно как решать,
# и мы разбиваем ее на меньшие задачи, которые тоже
# непонятно как решать. (с) А.Кумок

n = int(input())
inf = 1e9
cubes = [i ** 3 for i in range(1, 101)]
dp = [inf for _ in range(n + 1)]
dp[0] = 0
for i in range(1, n + 1):
    for j in cubes:
        if j > i:
            break
        dp[i] = min(dp[i], dp[i - j] + 1)
ans = dp[n]
print(ans)

