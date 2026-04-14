# ============================================================
# Problem   : #219 Contains Duplicate II
# Difficulty: Easy
# ============================================================
# Approach  : Sliding window of size k via a hash set
# Time      : O(n)
# Space     : O(k)
# Patterns  : HashMap, Sliding Window
# ============================================================
# Why optimal: We only care about the last k elements. A set of size ≤ k
# gives O(1) membership and O(1) eviction.
# ============================================================

from typing import List

class Solution:
    def containsNearbyDuplicate(self, nums: List[int], k: int) -> bool:
        window = set()
        for i, x in enumerate(nums):
            if x in window:
                return True
            window.add(x)
            if len(window) > k:             # evict the element that just fell out of window
                window.discard(nums[i - k])
        return False

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Dict of value→last index — Time: O(n) Space: O(n)
# Your current solution. Correct but has a bug: the `else: hs[nums[i]]=i`
# branch is unreachable because the elif already covered the "in hs" case.
# You update the index only on a "too far" match — good! But the overall
# structure is trickier than the sliding-set version.
#
# Approach 3: Brute force O(n*k) nested loop.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Contains Duplicate III — values within t and indices within k.
# Q2: What if k is huge (> n)? Does the set approach still win?
# Q3: Stream version — numbers arrive one at a time.
