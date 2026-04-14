# ============================================================
# Problem   : #20 Valid Parentheses
# Difficulty: Easy
# ============================================================
# Approach  : Stack + closer→opener map
# Time      : O(n)
# Space     : O(n)
# Patterns  : Stack, String
# ============================================================
# Why optimal: Push openers; on closer, pop and match. Empty stack at
# the end means balanced.
# ============================================================

class Solution:
    def isValid(self, s: str) -> bool:
        pair = {")": "(", "]": "[", "}": "{"}
        stack = []
        for ch in s:
            if ch in pair:                  # closer
                if not stack or stack.pop() != pair[ch]:
                    return False
            else:                            # opener
                stack.append(ch)
        return not stack

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Repeated string replace "()","[]","{}" → "" — Time: O(n^2) Space: O(n)
# Elegant but quadratic.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Minimum add to make valid (LC 921).
# Q2: Longest valid parentheses (LC 32).
# Q3: With wildcards '*' (LC 678).
