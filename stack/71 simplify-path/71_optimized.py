# ============================================================
# Problem   : #71 Simplify Path
# Difficulty: Medium
# ============================================================
# Approach  : Split on "/", walk parts, push/pop on a stack
# Time      : O(n)
# Space     : O(n)
# Patterns  : Stack, String
# ============================================================
# Why optimal: Each part is either a dir name (push), ".." (pop), ".",
# or empty (skip). One linear scan builds the canonical path.
# ============================================================

class Solution:
    def simplifyPath(self, path: str) -> str:
        stack = []
        for part in path.split("/"):
            if part == "" or part == ".":
                continue
            if part == "..":
                if stack:
                    stack.pop()
            else:
                stack.append(part)
        return "/" + "/".join(stack)

# ============================================================
# ALTERNATIVE APPROACHES
# ============================================================
# Approach 2: Manual two-pointer scan without split — O(n) Space: O(n)
# More verbose, no real benefit.

# ============================================================
# SDE 2 FOLLOW-UP QUESTIONS
# ============================================================
# Q1: Handle symlinks or Windows-style paths.
# Q2: Relative path resolution (given a base).
# Q3: What if `..` above root should error instead of staying at root?
