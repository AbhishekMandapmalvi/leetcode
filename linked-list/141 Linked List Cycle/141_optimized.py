# ============================================================
# Problem   : #141 Linked List Cycle
# Difficulty: Easy
# ============================================================
# Approach  : Floyd's tortoise and hare
# Time      : O(n)
# Space     : O(1)
# Patterns  : Linked List, Two Pointers
# ============================================================
# Why optimal: If there's a cycle, fast laps slow and they meet. No hash
# set means O(1) space.
# ============================================================

from typing import Optional

class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

class Solution:
    def hasCycle(self, head: Optional[ListNode]) -> bool:
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                return True
        return False

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Hash set of seen nodes — Time: O(n) Space: O(n)

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Find the node where the cycle begins (LC 142).
# Q2: How do you detect a cycle length?
# Q3: Extend to a directed graph — Floyd vs DFS-based detection.
