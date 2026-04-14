# ============================================================
# Problem   : #209 Minimum Size Subarray Sum
# Difficulty: Medium
# ============================================================
# Approach  : Expanding + shrinking sliding window
# Time      : O(n)
# Space     : O(1)
# Patterns  : Sliding Window
# ============================================================
# Why optimal: Because all nums are positive, the window sum is monotone
# in window size — we can safely shrink from the left whenever the sum
# meets the target. Each index is entered/left at most once → O(n).
# ============================================================

from typing import List

class Solution:
    def minSubArrayLen(self, target: int, nums: List[int]) -> int:
        l = 0
        s = 0
        best = float('inf')
        for r, x in enumerate(nums):
            s += x
            while s >= target:
                best = min(best, r - l + 1)
                s -= nums[l]
                l += 1
        return best if best != float('inf') else 0

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Prefix sum + binary search — Time: O(n log n) Space: O(n)
# For each i, binary search the smallest j with prefix[j]-prefix[i]>=target.
# Required when values can be negative.
#
# Approach 3: Brute force O(n^2).

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: What if nums can be negative? Why does the sliding window break?
# Q2: Longest subarray with sum >= target — how does the window change?
# Q3: Return the actual subarray, not just its length.
