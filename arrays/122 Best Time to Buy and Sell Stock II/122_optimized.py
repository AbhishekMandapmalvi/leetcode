# ============================================================
# Problem   : #122 Best Time to Buy and Sell Stock II
# Difficulty: Medium
# ============================================================
# Approach  : Sum every positive daily delta
# Time      : O(n)
# Space     : O(1)
# Patterns  : Array, Greedy
# ============================================================
# Why optimal: You can buy/sell any number of times. Any upward slope
# can be captured as a sum of daily positive deltas; no need to track
# explicit buy/sell pairs.
# ============================================================

from typing import List

class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        return sum(max(prices[i] - prices[i - 1], 0) for i in range(1, len(prices)))

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Peak-valley tracking — Time: O(n) Space: O(1)
# Walk until a local peak, sell; walk until a local valley, buy. Equivalent.
#
# Approach 3: DP with states (held/not held) — Time: O(n) Space: O(1)
# Generalizes to problems with fees or cooldowns.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: With a per-transaction fee (LC 714).
# Q2: With a cooldown day between sell and buy (LC 309).
# Q3: Prove that summing positive deltas equals the peak-valley strategy.
