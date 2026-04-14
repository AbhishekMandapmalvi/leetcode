# ============================================================
# Problem   : #206 Reverse Linked List
# Difficulty: Easy
# ============================================================
# Approach  : Iterative prev/curr pointer swap
# Time      : O(n)
# Space     : O(1)
# Patterns  : Linked List
# ============================================================
# Why optimal: One pass, three-pointer dance. Recursive version uses O(n)
# stack.
# ============================================================

from typing import Optional

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        prev, curr = None, head
        while curr:
            nxt = curr.next
            curr.next = prev
            prev = curr
            curr = nxt
        return prev

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Recursive — Time: O(n) Space: O(n) stack
# def rev(node): if not node.next: return node; new=rev(node.next); node.next.next=node; node.next=None; return new

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Reverse between positions m..n (LC 92).
# Q2: Reverse k-group (LC 25).
# Q3: Detect whether reversing yields a palindrome (LC 234).
