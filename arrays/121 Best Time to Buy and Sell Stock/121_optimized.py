# ============================================================
# Problem   : #121 Best Time to Buy and Sell Stock
# Difficulty: Easy
# ============================================================
# Approach  : Single pass, track running min price and max profit
# Time      : O(n)
# Space     : O(1)
# Patterns  : Array, Greedy
# ============================================================
# Why optimal: For each day, the best sell profit is `price - min_so_far`.
# Update both as we go.
# ============================================================

from typing import List

class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        lo = float('inf')
        best = 0
        for p in prices:
            lo = min(lo, p)
            best = max(best, p - lo)
        return best

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Brute force O(n^2).
# Approach 3: Kadane's on daily diffs — Time: O(n) Space: O(1)
# max subarray sum of (prices[i]-prices[i-1]) = best profit.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: At most 2 transactions (LC 123). At most k (LC 188).
# Q2: With cooldown (LC 309). With transaction fee (LC 714).
# Q3: Stream version — you don't see all prices at once.
