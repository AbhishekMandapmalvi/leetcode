# ============================================================
# Problem   : #347 Top K Frequent Elements
# Difficulty: Medium
# ============================================================
# Approach  : Bucket sort on frequency (indexed 0..n)
# Time      : O(n)
# Space     : O(n)
# Patterns  : HashMap, Heap
# ============================================================
# Why optimal: Frequencies are bounded by n, so we can index an array of
# lists by frequency and walk it from the top down. Beats heap O(n log k).
# ============================================================

from typing import List
from collections import Counter

class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        freq = Counter(nums)
        buckets = [[] for _ in range(len(nums) + 1)]
        for num, f in freq.items():
            buckets[f].append(num)          # freq is bounded by n
        out = []
        for f in range(len(buckets) - 1, 0, -1):
            out.extend(buckets[f])
            if len(out) >= k:
                return out[:k]
        return out[:k]

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Min-heap of size k — Time: O(n log k) Space: O(k)
# Your current solution. Clean, scales well for very large n with small k.
#
# Approach 3: Quickselect on (freq,num) — Time: O(n) avg Space: O(n)
# Best-known linear average; trickier to get right.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: What if ties matter (return smallest value among ties)?
# Q2: Stream: top k most frequent in a sliding window.
# Q3: Distributed version across many shards — how to merge top-k per shard?
