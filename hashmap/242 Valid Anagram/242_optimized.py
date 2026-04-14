# ============================================================
# Problem   : #242 Valid Anagram
# Difficulty: Easy
# ============================================================
# Approach  : Single counter, increment on s, decrement on t, check all zero
# Time      : O(n)
# Space     : O(1)   (bounded alphabet)
# Patterns  : HashMap, String
# ============================================================
# Why optimal: One pass over each string and one dict. Two-dict compare
# is fine but wasteful; a single 26-int array is even leaner for lowercase.
# ============================================================

from collections import Counter

class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        c = Counter(s)
        for ch in t:
            c[ch] -= 1
            if c[ch] < 0:                   # more of ch in t than in s
                return False
        return True

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Two dicts and compare — Time: O(n) Space: O(k)
# Your current solution. Correct, slightly more code.
#
# Approach 3: Sort and compare — Time: O(n log n) Space: O(n)
# Shortest code, slower.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Group Anagrams (LC 49) — extension across a list of strings.
# Q2: Unicode strings — can you still use a fixed-size array?
# Q3: Find all anagrams of p in s (LC 438) — sliding window version.
