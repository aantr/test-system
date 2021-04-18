inf = 1e9
maxn = 1000
dp = [[[[inf for _ in range(2)]
        for _ in range(2)]
       for _ in range(maxn + 1)]
      for _ in range(maxn + 1)]

s = input()
m = s.count('0')
n = len(s)
dp[0][0][0][0] = 0
for i in range(1, n + 1):
    for j in range(i + 1):
        dp[i][j][0][0] = min(dp[i - 1][j][0][0], dp[i - 1][j][0][1])
        dp[i][j][1][0] = min(dp[i - 1][j][1][0], dp[i - 1][j][1][1])

    for j in range(1, i + 1):
        dp[i][j][0][1] = int(s[i - 1] == '1') + dp[i - 1][j - 1][0][0]
        dp[i][j][1][1] = int(s[i - 1] == '1') + \
                         min(dp[i - 1][j - 1][0][1], dp[i - 1][j - 1][1][0])

res = min(dp[n][m][1][1], dp[n][m][1][0])
print(res if res != inf else -1)
