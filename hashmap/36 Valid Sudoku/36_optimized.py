# ============================================================
# Problem   : #36 Valid Sudoku
# Difficulty: Medium
# ============================================================
# Approach  : Track rows, cols, and 3x3 boxes with 9 hash sets each
# Time      : O(1)  (fixed 81 cells)
# Space     : O(1)
# Patterns  : HashMap, Matrix
# ============================================================
# Why optimal: One pass. Each cell is checked against three sets (row,
# col, box) and then added. box_index = (r//3)*3 + (c//3).
# ============================================================

from typing import List

class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        rows  = [set() for _ in range(9)]
        cols  = [set() for _ in range(9)]
        boxes = [set() for _ in range(9)]
        for r in range(9):
            for c in range(9):
                v = board[r][c]
                if v == ".":
                    continue
                b = (r // 3) * 3 + (c // 3)
                if v in rows[r] or v in cols[c] or v in boxes[b]:
                    return False
                rows[r].add(v)
                cols[c].add(v)
                boxes[b].add(v)
        return True

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Encode (v,r), (v,c), (v,box) as strings into one set — Time: O(1) Space: O(1)
# Clever one-pass with a single set.
#
# Approach 3: Bitmask per row/col/box — Time: O(1) Space: O(1)
# 9 bits per mask; fastest in practice.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Sudoku Solver (LC 37) — extend to backtracking.
# Q2: What if the board is N x N with sqrt(N) x sqrt(N) boxes (N=16, 25)?
# Q3: How would you validate concurrently across rows/cols/boxes?
