# ============================================================
# Problem   : #290 Word Pattern
# Difficulty: Easy
# ============================================================
# Approach  : Two hash maps (char→word and word→char) enforcing bijection
# Time      : O(n)
# Space     : O(n)
# Patterns  : HashMap, String
# ============================================================
# Why optimal: Exactly Isomorphic Strings (LC 205) but on word tokens
# instead of characters. Two maps guarantee injectivity in both directions.
# ============================================================

class Solution:
    def wordPattern(self, pattern: str, s: str) -> bool:
        words = s.split()
        if len(pattern) != len(words):
            return False
        c_w, w_c = {}, {}
        for c, w in zip(pattern, words):
            if c in c_w:
                if c_w[c] != w:
                    return False
            elif w in w_c:
                return False
            else:
                c_w[c] = w
                w_c[w] = c
        return True

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Compare index signatures — Time: O(n) Space: O(n)
# Transform both sequences to their "first-occurrence index" tuples and compare.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: What if words contain punctuation or mixed case?
# Q2: Word Pattern II — can you split `s` into a pattern-matching tokenization?
# Q3: Can you do it with a single dict + a set of used values?
