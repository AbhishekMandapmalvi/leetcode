# ============================================================
# Problem   : #125 Valid Palindrome
# Difficulty: Easy
# ============================================================
# Approach  : In-place two pointers, skip non-alphanumerics, compare lowercased
# Time      : O(n)
# Space     : O(1)
# Patterns  : Two Pointers, String
# ============================================================
# Why optimal: No extra buffer. We walk both ends toward the middle,
# skipping junk characters on the fly, and fail fast on the first mismatch.
# ============================================================

class Solution:
    def isPalindrome(self, s: str) -> bool:
        l, r = 0, len(s) - 1
        while l < r:
            if not s[l].isalnum():          # skip left junk
                l += 1
            elif not s[r].isalnum():        # skip right junk
                r -= 1
            elif s[l].lower() != s[r].lower():
                return False
            else:
                l += 1
                r -= 1
        return True

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Filter + reverse compare — Time: O(n) Space: O(n)
# cleaned = [c.lower() for c in s if c.isalnum()]; return cleaned == cleaned[::-1]
#
# Approach 3: Regex clean + slice — Time: O(n) Space: O(n)
# t = re.sub(r'[^a-z0-9]', '', s.lower()); return t == t[::-1]

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: How would you handle Unicode (accents, non-ASCII alphanumerics)?
# Q2: Stream version — input is a generator, not an indexable string.
# Q3: Palindrome with at most k character edits allowed (valid palindrome II/III).
