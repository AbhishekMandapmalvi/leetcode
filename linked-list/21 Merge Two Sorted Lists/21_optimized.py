# ============================================================
# Problem   : #21 Merge Two Sorted Lists
# Difficulty: Easy
# ============================================================
# Approach  : Dummy head + splice the smaller current node
# Time      : O(m + n)
# Space     : O(1)
# Patterns  : Linked List, Merge
# ============================================================
# Why optimal: Reuses existing nodes (no allocation) and avoids edge
# cases via the dummy head. Attach the leftover tail at the end.
# ============================================================

from typing import Optional

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def mergeTwoLists(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode()
        tail = dummy
        while l1 and l2:
            if l1.val <= l2.val:
                tail.next, l1 = l1, l1.next
            else:
                tail.next, l2 = l2, l2.next
            tail = tail.next
        tail.next = l1 or l2                 # attach whatever's left
        return dummy.next

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Recursive — Time: O(m+n) Space: O(m+n) stack
# Elegant but uses stack proportional to total length.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Merge k sorted lists (LC 23) — heap or divide & conquer.
# Q2: Merge in-place without using any extra node allocation.
# Q3: Stable sort on a linked list.
