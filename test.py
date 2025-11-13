import heapq
from typing import List


class Solution:
    def maximalSquare(self, matrix: List[List[str]]) -> int:
        row_continue_one_cnt = [[0 for j in range(len(matrix[0]))] for i in range(len(matrix))]
        col_continue_one_cnt = [[0 for j in range(len(matrix[0]))] for i in range(len(matrix))]

        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if j == 0:
                    row_continue_one_cnt[i][j] = 1 if matrix[i][j] == '1' else 0
                else:
                    row_continue_one_cnt[i][j] = (1 + row_continue_one_cnt[i][j - 1]) if matrix[i][j] == '1' else 0
                if i == 0:
                    col_continue_one_cnt[i][j] = 1 if matrix[i][j] == '1' else 0
                else:
                    col_continue_one_cnt[i][j] = (1 + col_continue_one_cnt[i - 1][j]) if matrix[i][j] == '1' else 0

        endpoint_square_max_length = [[0 for j in range(len(matrix[0]))] for i in range(len(matrix))]

        final_max_length = 0
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                a = row_continue_one_cnt[i][j] - 1
                b = col_continue_one_cnt[i][j] - 1
                if i == 0 or j == 0:
                    c = 0
                c = endpoint_square_max_length[i - 1][j - 1]
                tmp_length = min([a, b, c]) + 1
                tmp_length = max(final_max_length, tmp_length)
                endpoint_square_max_length[i][j] = tmp_length
        return final_max_length ** 2


if __name__ == '__main__':

    sol = Solution()
    print(sol.maximalSquare([["1","0","1","0","0"],["1","0","1","1","1"],["1","1","1","1","1"],["1","0","0","1","0"]]))

