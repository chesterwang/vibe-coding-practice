from heapq import heappop
from typing import List


class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        min_num = [float('inf')]
        coins = sorted(coins, reverse=True)
        path = []
        result = []
        depth = 0
        self.dfs(path, depth, min_num, coins, amount)
        return -1 if min_num[0] == float('inf') else min_num[0]

    def dfs(self, path, depth, min_num, coins, amount):
        if sum(path) == amount:
            if len(path) < min_num[0]:
                min_num[0] = len(path)
                return
            else:
                return
        if depth >= len(coins):
            return False
        if len(path) >= min_num[0]:
            return False
        if sum(path) > amount:
            return False
        top_num = (amount - sum(path)) // coins[depth]
        tmp_num = top_num
        while tmp_num >=0:
            path += [coins[depth]] * tmp_num
            flag = self.dfs(path, depth + 1, min_num, coins, amount)
            [path.pop() for idx in range(0, tmp_num)]
            if flag == False:
                break
            tmp_num -= 1
a = dict()

a.


if __name__ == '__main__':
    # a = 'asdf'
    # print(a[:0]+'1' + a[1:])
    sol = Solution()
    print(sol.coinChange([411,412,413,414,415,416,417,418,419,420,421,422],9864))

