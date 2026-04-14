# ============================================================
# Problem   : #128 Longest Consecutive Sequence
# Difficulty: Medium
# ============================================================
# Approach  : Hash set + only start counting from sequence heads
# Time      : O(n)
# Space     : O(n)
# Patterns  : HashMap
# ============================================================
# Why optimal: Put all numbers in a set. A number `x` is the START of a
# run only if `x-1` is not in the set. Walk forward from each head; each
# element is touched at most twice total → O(n).
# ============================================================

from typing import List

class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        s = set(nums)                       # O(1) membership
        best = 0
        for x in s:
            if x - 1 in s:                  # not a run head; skip
                continue
            length = 1
            y = x + 1
            while y in s:                   # extend run
                length += 1
                y += 1
            best = max(best, length)
        return best

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Sort + scan — Time: O(n log n) Space: O(1) (or O(n) for sort)
# After sorting, track current run length, reset on gaps, skip duplicates.
#
# Approach 3: Your boundary-dict trick — Time: O(n) Space: O(n)
# Correct but trickier to reason about and easier to get wrong than the set method.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Return the actual longest run, not just the length.
# Q2: Stream version — numbers arrive one at a time.
# Q3: How does Union-Find compare in complexity and code clarity?
