# ============================================================
# Problem   : #1 Two Sum
# Difficulty: Easy
# ============================================================
# Approach  : One-pass hash map of value → index
# Time      : O(n)
# Space     : O(n)
# Patterns  : HashMap
# ============================================================
# Why optimal: A single scan that checks for the complement before
# inserting the current value. Brute force is O(n^2); sort + two-pointer
# is O(n log n) and loses original indices.
# ============================================================

from typing import List

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}                           # value -> index
        for i, x in enumerate(nums):
            if target - x in seen:          # complement seen earlier?
                return [seen[target - x], i]
            seen[x] = i
        return []

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Brute force — Time: O(n^2) Space: O(1)
# for i,j with i<j: check nums[i]+nums[j]==target.
#
# Approach 3: Sort + two pointers — Time: O(n log n) Space: O(n) (to track original indices)

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Return ALL unique pairs that sum to target (not just one).
# Q2: What if the array is streamed and you can't store everything?
# Q3: Two Sum in a sorted array — best approach?
