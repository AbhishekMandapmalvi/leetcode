# ============================================================
# Problem   : #189 Rotate Array
# Difficulty: Medium
# ============================================================
# Approach  : Triple reverse (in-place, O(1) space)
# Time      : O(n)
# Space     : O(1)
# Patterns  : Array, In-place
# ============================================================
# Why optimal: Slicing uses O(n) extra space. The reverse trick is the
# canonical O(1) in-place rotation:
#   1. Reverse the whole array.
#   2. Reverse the first k.
#   3. Reverse the rest.
# ============================================================

from typing import List

class Solution:
    def rotate(self, nums: List[int], k: int) -> None:
        n = len(nums)
        k %= n
        self._rev(nums, 0, n - 1)
        self._rev(nums, 0, k - 1)
        self._rev(nums, k, n - 1)

    def _rev(self, a, i, j):
        while i < j:
            a[i], a[j] = a[j], a[i]
            i += 1
            j -= 1

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Slice and paste — Time: O(n) Space: O(n)
# Your current solution. Correct; uses O(n) extra.
#
# Approach 3: Cyclic replacements — Time: O(n) Space: O(1)
# Walk gcd(n,k) cycles; tricky to get right.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Prove the triple-reverse identity.
# Q2: Rotate a 2D matrix 90 degrees.
# Q3: Rotate a linked list by k.
