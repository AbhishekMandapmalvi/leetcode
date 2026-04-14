# ============================================================
# Problem   : #49 Group Anagrams
# Difficulty: Medium
# ============================================================
# Approach  : Group by char-count tuple key (26 ints)
# Time      : O(n * k)   n strings of length k
# Space     : O(n * k)
# Patterns  : HashMap, String
# ============================================================
# Why optimal: Sorting each string is O(k log k); a tuple of 26 counts is
# O(k) per string and produces the same grouping key.
# ============================================================

from typing import List
from collections import defaultdict

class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        groups = defaultdict(list)
        for s in strs:
            counts = [0] * 26
            for ch in s:
                counts[ord(ch) - ord('a')] += 1
            groups[tuple(counts)].append(s)
        return list(groups.values())

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Sort each string as the key — Time: O(n * k log k) Space: O(n * k)
# Your current solution. Simpler to write, slightly slower.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Anagrams of Unicode strings — how do you build the key?
# Q2: Stream version — groups must be reported as they emerge.
# Q3: What if k is very large? Which approach wins asymptotically?
