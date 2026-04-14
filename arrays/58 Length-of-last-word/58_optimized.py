# ============================================================
# Problem   : #58 Length of Last Word
# Difficulty: Easy
# ============================================================
# Approach  : Scan from the right, skip trailing spaces, count word chars
# Time      : O(n)
# Space     : O(1)
# Patterns  : Array, String
# ============================================================
# Why optimal: We only need the last word; walking from the end avoids
# processing the entire string.
# ============================================================

class Solution:
    def lengthOfLastWord(self, s: str) -> int:
        i = len(s) - 1
        while i >= 0 and s[i] == " ":
            i -= 1
        count = 0
        while i >= 0 and s[i] != " ":
            count += 1
            i -= 1
        return count

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: One-liner — Time: O(n) Space: O(n)
# return len(s.split()[-1]) if s.split() else 0

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Return the last word itself, not just its length.
# Q2: Length of the k-th word from the end.
# Q3: Handle multi-byte whitespace (Unicode).
