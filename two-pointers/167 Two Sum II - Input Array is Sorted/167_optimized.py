# ============================================================
# Problem   : #167 Two Sum II - Input Array is Sorted
# Difficulty: Medium
# ============================================================
# Approach  : Two pointers from both ends, shrink based on sum vs target
# Time      : O(n)
# Space     : O(1)
# Patterns  : Two Pointers, Binary Search
# ============================================================
# Why optimal: The sorted property lets us move monotonically: if the sum
# is too small, only increasing the left value can help; if too big, only
# decreasing the right value can help. Each element is visited at most once.
# ============================================================

from typing import List

class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        l, r = 0, len(numbers) - 1
        while l < r:
            s = numbers[l] + numbers[r]
            if s == target:
                return [l + 1, r + 1]   # problem uses 1-indexed
            if s < target:
                l += 1
            else:
                r -= 1
        return []  # unreachable per problem guarantees

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: HashMap — Time: O(n) Space: O(n)
# Works but ignores the sorted-ness; worse space.
#
# Approach 3: Binary search the complement for each i — Time: O(n log n) Space: O(1)
# for i in range(n): bsearch for target-numbers[i] in numbers[i+1:].

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: What if there are duplicates and multiple valid pairs exist?
# Q2: Unsorted array — is it still better to sort + two-pointer, or hash?
# Q3: Extend to 3Sum / kSum on sorted input — complexity tradeoffs.
