# ============================================================
# Problem   : #205 Isomorphic Strings
# Difficulty: Easy
# ============================================================
# Approach  : Two hash maps enforcing a bijection between chars
# Time      : O(n)
# Space     : O(1)  (ASCII/unicode char set bounded)
# Patterns  : HashMap, String
# ============================================================
# Why optimal: A single map (s→t) allows different s chars to map to the
# same t char, breaking isomorphism. Two maps (s→t and t→s) enforce
# injectivity both ways in one linear pass.
# ============================================================

class Solution:
    def isIsomorphic(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        s_t, t_s = {}, {}
        for a, b in zip(s, t):
            if a in s_t:
                if s_t[a] != b:             # a already mapped to a different char
                    return False
            elif b in t_s:                  # b already used by a different a
                return False
            else:
                s_t[a] = b
                t_s[b] = a
        return True

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Compare index patterns — Time: O(n) Space: O(n)
# Transform each string to the sequence of first-occurrence indices; compare.
#
# Approach 3: Single dict s→t + set of used targets — Time: O(n) Space: O(1)
# Equivalent, just phrased differently.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Word Pattern (LC 290) — same problem on word tokens. How do you reuse this?
# Q2: Case-insensitive isomorphism?
# Q3: What about Unicode grapheme clusters (emoji, combining marks)?
