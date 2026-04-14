# ============================================================
# Problem   : #217 Contains Duplicate
# Difficulty: Easy
# ============================================================
# Approach  : Compare set size to list size
# Time      : O(n)
# Space     : O(n)
# Patterns  : HashMap
# ============================================================
# Why optimal: One-liner that stops as soon as Python's set builder
# detects enough structure. You can also early-return on first collision.
# ============================================================

from typing import List

class Solution:
    def containsDuplicate(self, nums: List[int]) -> bool:
        return len(set(nums)) != len(nums)

    # Early-exit version (slightly better on duplicate-heavy inputs):
    def containsDuplicate_earlyExit(self, nums: List[int]) -> bool:
        seen = set()
        for x in nums:
            if x in seen:
                return True
            seen.add(x)
        return False

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Sort and check neighbors — Time: O(n log n) Space: O(1)
# Useful if you must avoid O(n) extra space.
#
# Approach 3: Bit set — Time: O(n) Space: O(max/64)
# Only when values are small integers.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Contains Duplicate II (LC 219) — same element within k distance.
# Q2: Contains Duplicate III — value within t and index within k.
# Q3: Can you do it in O(1) extra space without sorting (hint: impossible in general)?
