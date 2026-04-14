# ============================================================
# Problem   : #56 Merge Intervals
# Difficulty: Medium
# ============================================================
# Approach  : Sort by start; extend last merged end on overlap
# Time      : O(n log n)
# Space     : O(n)
# Patterns  : Array, Intervals, Sorting
# ============================================================
# Why optimal: After sorting by start, any overlap must touch the last
# merged interval's end — we never need to look further back.
# ============================================================

from typing import List

class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        intervals.sort(key=lambda x: x[0])
        out = [intervals[0]]
        for start, end in intervals[1:]:
            if start <= out[-1][1]:         # overlap
                out[-1][1] = max(out[-1][1], end)
            else:
                out.append([start, end])
        return out

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Sweep line on (time, type) events — Time: O(n log n) Space: O(n)
# Useful if you also need counts or overlap depth.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Insert Interval (LC 57) — input already sorted, insert one and merge.
# Q2: Meeting Rooms II (LC 253) — min rooms == max concurrent intervals.
# Q3: How would you parallelize across shards?
