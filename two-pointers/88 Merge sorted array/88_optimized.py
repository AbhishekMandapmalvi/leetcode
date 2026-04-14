# ============================================================
# Problem   : #88 Merge Sorted Array
# Difficulty: Easy
# ============================================================
# Approach  : Three pointers from the END of both arrays
# Time      : O(m + n)
# Space     : O(1)
# Patterns  : Two Pointers, Merge
# ============================================================
# Why optimal: Writing from the back avoids overwriting unread elements
# in nums1. Each step places the larger of the two current values at
# nums1[write], so we touch every slot exactly once.
# ============================================================

from typing import List

class Solution:
    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
        i, j, w = m - 1, n - 1, m + n - 1       # read m, read n, write at tail
        while j >= 0:                            # only need j; if i runs out, copy remaining nums2
            if i >= 0 and nums1[i] > nums2[j]:
                nums1[w] = nums1[i]
                i -= 1
            else:
                nums1[w] = nums2[j]
                j -= 1
            w -= 1

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Copy nums2 into tail of nums1, then bubble-sort neighbors — Time: O((m+n)^2) Space: O(1)
# Your current solution. Correct but quadratic.
#
# Approach 3: Merge into a new array then copy back — Time: O(m+n) Space: O(m+n)
# Simple, extra space.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Why merge from the back and not the front?
# Q2: What if nums1 did NOT have trailing capacity — how would you merge?
# Q3: Merge k sorted arrays — how does this generalize?
