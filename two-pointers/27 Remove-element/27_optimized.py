# ============================================================
# Problem   : #27 Remove Element
# Difficulty: Easy
# ============================================================
# Approach  : Fast/slow two pointers, overwrite in place
# Time      : O(n)
# Space     : O(1)
# Patterns  : Two Pointers, In-place
# ============================================================
# Why optimal: pop(i) from a list is O(n) per call, so repeated popping
# is O(n^2). The classic fast/slow trick writes kept elements to a slow
# index while a fast index scans — one pass, no shifting.
# ============================================================

from typing import List

class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        k = 0                       # slow pointer: next write slot
        for x in nums:              # fast pointer: scan
            if x != val:
                nums[k] = x
                k += 1
        return k

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: pop() in a while loop — Time: O(n^2) Space: O(1)
# Your current solution. Correct but quadratic because list.pop(i) shifts.
#
# Approach 3: Two-pointer swap-with-end — Time: O(n) Space: O(1)
# When order doesn't matter: swap matches to the tail, shrink length.
# Minimizes writes when val is rare.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: What if val appears very rarely — can you do fewer writes?
# Q2: Preserve order vs not — how does that change the choice of approach?
# Q3: Generalize to "remove all elements matching a predicate."
