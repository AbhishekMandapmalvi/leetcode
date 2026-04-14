# ============================================================
# Problem   : #2 Add Two Numbers
# Difficulty: Medium
# ============================================================
# Approach  : Dummy head + carry, walk both lists
# Time      : O(max(m, n))
# Space     : O(1)   (excluding output)
# Patterns  : Linked List
# ============================================================
# Why optimal: A single pass, treating missing digits as 0 and propagating
# carry. The dummy head removes special-case logic for the first node.
# ============================================================

from typing import Optional

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode()
        tail = dummy
        carry = 0
        while l1 or l2 or carry:
            a = l1.val if l1 else 0
            b = l2.val if l2 else 0
            total = a + b + carry
            carry, digit = divmod(total, 10)
            tail.next = ListNode(digit)
            tail = tail.next
            if l1: l1 = l1.next
            if l2: l2 = l2.next
        return dummy.next

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Convert to ints, add, convert back — Time: O(n) Space: O(n)
# Breaks on huge numbers (outside long range).
#
# Approach 3: Recursive — same time, uses call stack.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: What if digits are stored MSB-first instead of LSB-first (LC 445)?
# Q2: What if one list is much longer — can you short-circuit?
# Q3: How would you do arbitrary base b instead of base 10?
