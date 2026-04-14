# ============================================================
# Problem   : #15 3Sum
# Difficulty: Medium
# ============================================================
# Approach  : Sort, fix one index, two-pointer sweep for the pair
# Time      : O(n^2)
# Space     : O(1) extra (ignoring output)
# Patterns  : Two Pointers, Sorting
# ============================================================
# Why optimal: Sorting lets us both (a) skip duplicates trivially by
# comparing to the previous element, and (b) use the monotonic two-pointer
# move to find the complementary pair in O(n), collapsing the inner two
# loops into one linear sweep. Total O(n^2).
# ============================================================

from typing import List

class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        nums.sort()
        res = []
        n = len(nums)
        for i in range(n - 2):
            if nums[i] > 0:                       # all remaining are positive
                break
            if i > 0 and nums[i] == nums[i - 1]:  # skip duplicate anchors
                continue
            l, r = i + 1, n - 1
            while l < r:
                s = nums[i] + nums[l] + nums[r]
                if s < 0:
                    l += 1
                elif s > 0:
                    r -= 1
                else:
                    res.append([nums[i], nums[l], nums[r]])
                    l += 1
                    r -= 1
                    while l < r and nums[l] == nums[l - 1]:  # skip dup lefts
                        l += 1
                    while l < r and nums[r] == nums[r + 1]:  # skip dup rights
                        r -= 1
        return res

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: HashSet on (i, j) pairs — Time: O(n^2) Space: O(n)
# Your current solution uses this: for each i, a set tracks seen values.
# Correct but uses extra space and needs careful dedup.
#
# Approach 3: Brute force triples — Time: O(n^3) Space: O(1)
# for i,j,k check sum == 0, dedup with a set of tuples.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Generalize to kSum — what's the recursive structure and complexity?
# Q2: 3Sum closest — find the triple whose sum is nearest to a target.
# Q3: How would you parallelize this for a huge array across N workers?
