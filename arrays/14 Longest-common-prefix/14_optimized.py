# ============================================================
# Problem   : #14 Longest Common Prefix
# Difficulty: Easy
# ============================================================
# Approach  : Sort lexicographically and compare only first vs last
# Time      : O(n log n * k)   (sort) or O(n * k) with vertical scan
# Space     : O(1)
# Patterns  : Array, String
# ============================================================
# Why optimal: After sorting, only the first and last strings matter:
# their common prefix is the prefix common to all. Vertical scan variant
# beats sort on time when n is small relative to string length.
# ============================================================

from typing import List

class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        if not strs:
            return ""
        strs.sort()
        a, b = strs[0], strs[-1]
        i = 0
        while i < min(len(a), len(b)) and a[i] == b[i]:
            i += 1
        return a[:i]

    # Vertical scan alt:
    def longestCommonPrefix_vertical(self, strs: List[str]) -> str:
        for i, chars in enumerate(zip(*strs)):
            if len(set(chars)) > 1:
                return strs[0][:i]
        return min(strs, key=len) if strs else ""

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Vertical scan — Time: O(n*k) Space: O(1)
# Approach 3: Divide and conquer / trie — overkill here.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Longest common suffix instead.
# Q2: What if strings are extremely long and n is small?
# Q3: Trie-based approach and its tradeoffs.
