# ============================================================
# Problem   : #3 Longest Substring Without Repeating Characters
# Difficulty: Medium
# ============================================================
# Approach  : Sliding window with last-seen dict — jump l past duplicates
# Time      : O(n)
# Space     : O(k)   (alphabet size)
# Patterns  : Sliding Window, HashMap
# ============================================================
# Why optimal: Instead of shrinking one char at a time, jump `l` directly
# past the last occurrence of the repeated char.
# ============================================================

class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        last = {}                           # char -> last seen index
        l = 0
        best = 0
        for r, ch in enumerate(s):
            if ch in last and last[ch] >= l:
                l = last[ch] + 1            # jump past the duplicate
            last[ch] = r
            best = max(best, r - l + 1)
        return best

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Sliding window with set, shrink one char at a time — O(n) O(k)
# Your O(N).py solution. Correct but more awkward (rebuilds temp list).
#
# Approach 3: Brute force O(n^2) or O(n^3).

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Longest substring with at most k distinct characters (LC 340).
# Q2: Longest substring with exactly k distinct characters.
# Q3: Unicode / emoji — does the dict approach still work?
