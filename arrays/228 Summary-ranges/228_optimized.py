# ============================================================
# Problem   : #228 Summary Ranges
# Difficulty: Easy
# ============================================================
# Approach  : Walk, extend runs, emit start or start->end
# Time      : O(n)
# Space     : O(1)  (excluding output)
# Patterns  : Array, Intervals
# ============================================================
# Why optimal: One pass. Each run is detected by `nums[i+1] == nums[i]+1`.
# ============================================================

from typing import List

class Solution:
    def summaryRanges(self, nums: List[int]) -> List[str]:
        out = []
        i = 0
        n = len(nums)
        while i < n:
            start = nums[i]
            while i + 1 < n and nums[i + 1] == nums[i] + 1:
                i += 1
            out.append(str(start) if start == nums[i] else f"{start}->{nums[i]}")
            i += 1
        return out

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Collect breakpoints and format — Time: O(n) Space: O(n)

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Missing Ranges (LC 163) — complementary problem.
# Q2: What if the input contains duplicates?
# Q3: Extend to floating-point or arbitrary comparators.
