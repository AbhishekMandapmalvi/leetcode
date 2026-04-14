# ============================================================
# Problem   : #383 Ransom Note
# Difficulty: Easy
# ============================================================
# Approach  : Counter(magazine) - Counter(ransom) empty check
# Time      : O(n + m)
# Space     : O(1)   (fixed alphabet)
# Patterns  : HashMap, String
# ============================================================
# Why optimal: Count supply, subtract demand; fail if any char goes
# negative. Cleaner than two dicts.
# ============================================================

from collections import Counter

class Solution:
    def canConstruct(self, ransomNote: str, magazine: str) -> bool:
        supply = Counter(magazine)
        for ch in ransomNote:
            if supply[ch] == 0:
                return False
            supply[ch] -= 1
        return True

    # One-liner:
    def canConstruct_oneline(self, ransomNote: str, magazine: str) -> bool:
        return not (Counter(ransomNote) - Counter(magazine))

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Sort both, scan with two pointers — Time: O(n log n) Space: O(1)

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: What if letters can be reused?
# Q2: What if you care about which magazine letters were used?
# Q3: Unicode / multi-byte characters — does Counter still work?
