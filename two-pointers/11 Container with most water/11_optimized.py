# ============================================================
# Problem   : #11 Container With Most Water
# Difficulty: Medium
# ============================================================
# Approach  : Two pointers from both ends, move the shorter wall inward
# Time      : O(n)
# Space     : O(1)
# Patterns  : Two Pointers, Greedy
# ============================================================
# Why optimal: Area is bounded by the shorter wall. Moving the taller
# wall inward can never increase the area (width shrinks, height capped
# by the same short side), so we always move the shorter one — this
# prunes O(n^2) brute force to a single linear sweep.
# ============================================================

from typing import List

class Solution:
    def maxArea(self, height: List[int]) -> int:
        l, r = 0, len(height) - 1           # pointers at both ends
        best = 0
        while l < r:
            h = min(height[l], height[r])   # area capped by shorter wall
            best = max(best, h * (r - l))
            if height[l] < height[r]:       # move the shorter side
                l += 1
            else:
                r -= 1
        return best

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Brute force all pairs — Time: O(n^2) Space: O(1)
# for i in range(n): for j in range(i+1, n): track max (i-j)*min(h[i],h[j])
#
# Approach 3: Divide & conquer on max heights — Time: O(n log n) Space: O(log n)
# Not practical here; two-pointer dominates.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Prove why moving the taller pointer can never yield a larger area.
# Q2: What if heights can be negative or zero? Does the invariant still hold?
# Q3: How would you adapt this to return the indices of the optimal pair
#     when there are ties? What about streaming input?
