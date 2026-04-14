# ============================================================
# Problem   : #45 Jump Game II
# Difficulty: Medium
# ============================================================
# Approach  : BFS in layers — track current jump's reachable end
# Time      : O(n)
# Space     : O(1)
# Patterns  : Greedy, Array
# ============================================================
# Why optimal: Think of each jump as a BFS layer. `end` marks the
# farthest index reachable on the current jump; `farthest` is the best
# we can reach if we extend one more jump. When `i == end`, commit a jump.
# ============================================================

from typing import List

class Solution:
    def jump(self, nums: List[int]) -> int:
        jumps = 0
        end = 0                 # current layer's boundary
        farthest = 0            # next layer's farthest reachable
        for i in range(len(nums) - 1):
            farthest = max(farthest, i + nums[i])
            if i == end:        # must jump to extend reach
                jumps += 1
                end = farthest
        return jumps

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: BFS with queue — Time: O(n) Space: O(n)
# Same idea, more overhead.
#
# Approach 3: DP — Time: O(n^2) Space: O(n)
# min_jumps[i] = min over reachable j of min_jumps[j]+1.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: What if some cells are forbidden?
# Q2: Return the actual sequence of indices jumped to.
# Q3: What if jump sizes can be negative (teleporter-style)?
