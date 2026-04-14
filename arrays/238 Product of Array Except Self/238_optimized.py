# ============================================================
# Problem   : #238 Product of Array Except Self
# Difficulty: Medium
# ============================================================
# Approach  : Left-product pass, then right-product pass, reusing output
# Time      : O(n)
# Space     : O(1)  (output array doesn't count)
# Patterns  : Array, Prefix Sum
# ============================================================
# Why optimal: Division isn't allowed. Prefix products from the left
# and suffix products from the right combine into the answer in two
# passes without an extra array.
# ============================================================

from typing import List

class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        n = len(nums)
        out = [1] * n
        left = 1
        for i in range(n):                  # out[i] = product of nums[:i]
            out[i] = left
            left *= nums[i]
        right = 1
        for i in range(n - 1, -1, -1):      # multiply in product of nums[i+1:]
            out[i] *= right
            right *= nums[i]
        return out

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Two extra arrays (left[], right[]) — Time: O(n) Space: O(n)
# Conceptually clearest; worse space.
#
# Approach 3: With division — Time: O(n) Space: O(1)
# Not allowed by the problem, but worth discussing (fails on zeros).

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Handle division when there's at most one zero.
# Q2: What about streaming input?
# Q3: 2D version — product of all entries except the row and column.
