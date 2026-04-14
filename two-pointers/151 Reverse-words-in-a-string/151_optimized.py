# ============================================================
# Problem   : #151 Reverse Words in a String
# Difficulty: Medium
# ============================================================
# Approach  : split() collapses whitespace, reverse, rejoin
# Time      : O(n)
# Space     : O(n)
# Patterns  : String, Two Pointers
# ============================================================
# Why optimal: Python's split() with no args already normalizes runs of
# whitespace, so the one-liner is the cleanest O(n) answer. The manual
# two-pointer in-place version is only interesting in languages where
# strings are mutable (C++/C).
# ============================================================

class Solution:
    def reverseWords(self, s: str) -> str:
        return " ".join(s.split()[::-1])    # split collapses spaces, reverse, rejoin

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Manual scan + stack — Time: O(n) Space: O(n)
# Walk s, accumulate word chars, push onto stack on space; pop to build result.
#
# Approach 3: In-place on char array (C++ style) — Time: O(n) Space: O(1)
# 1. Reverse whole array. 2. Reverse each word in place. 3. Compact spaces.
# The canonical interview answer when asked "no extra space."

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Do it in-place on a char array without using split().
# Q2: Preserve multiple internal spaces instead of collapsing them.
# Q3: Reverse words in a streamed log line where lines can be very long.
