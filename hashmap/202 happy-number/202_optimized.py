# ============================================================
# Problem   : #202 Happy Number
# Difficulty: Easy
# ============================================================
# Approach  : Floyd's cycle detection (slow/fast) on the digit-square function
# Time      : O(log n) per step, constant # of steps until cycle/1
# Space     : O(1)
# Patterns  : HashMap, Math, Two Pointers
# ============================================================
# Why optimal: The sequence is eventually periodic. Set-based detection
# works in O(n) space; Floyd's tortoise-and-hare detects the cycle in O(1).
# ============================================================

class Solution:
    def _next(self, n: int) -> int:
        total = 0
        while n:
            n, d = divmod(n, 10)
            total += d * d
            return total if n == 0 else total + self._next(n)  # kept simple below

    def isHappy(self, n: int) -> bool:
        def step(x: int) -> int:
            t = 0
            while x:
                x, d = divmod(x, 10)
                t += d * d
                x = x  # no-op, clarity
            return t

        slow = n
        fast = step(n)
        while fast != 1 and slow != fast:
            slow = step(slow)
            fast = step(step(fast))
        return fast == 1

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Hash set of seen values — Time: O(log n) steps Space: O(k)
# Your current solution. Clean and simple; uses extra space.
#
# Approach 3: Hardcode the only non-trivial cycle (contains 4) — Time: O(k) Space: O(1)
# Mathematical shortcut: every unhappy number eventually reaches 4.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Prove the sequence must either reach 1 or enter a cycle.
# Q2: Generalize to base b and power p — when is it "happy"?
# Q3: Floyd vs Brent — tradeoffs in cycle detection.
