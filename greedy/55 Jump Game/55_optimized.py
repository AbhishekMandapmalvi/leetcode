# ============================================================
# Problem   : #55 Jump Game
# Difficulty: Medium
# ============================================================
# Approach  : Greedy forward — track the farthest reachable index
# Time      : O(n)
# Space     : O(1)
# Patterns  : Greedy, Array
# ============================================================
# Why optimal: Walk forward. If at index i, i > farthest_reachable,
# we're stuck. Otherwise update farthest = max(farthest, i + nums[i]).
# ============================================================

from typing import List

class Solution:
    def canJump(self, nums: List[int]) -> bool:
        farthest = 0
        for i, x in enumerate(nums):
            if i > farthest:
                return False
            farthest = max(farthest, i + x)
        return True

    # Backward version (your solution):
    def canJump_backward(self, nums: List[int]) -> bool:
        last = len(nums) - 1
        for i in range(len(nums) - 1, -1, -1):
            if i + nums[i] >= last:
                last = i
        return last == 0

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: DP O(n^2)
# reachable[i] = any reachable[j] with j+nums[j]>=i.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Jump Game II — return min jumps.
# Q2: Jump Game III — jump i±nums[i], reach any 0.
# Q3: Jump Game with restricted max step.
