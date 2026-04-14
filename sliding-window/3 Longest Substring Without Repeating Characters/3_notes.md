# #3 — Longest Substring Without Repeating Characters

> **Difficulty:** Medium | **Patterns:** Sliding Window, HashMap | **Date:** 2026-04-13

**My approach:** Two pointers with a `temp` list, rebuild when a duplicate shows up.

**Where I went off track:** Rebuilding the `temp` list every collision is wasteful. The clean version keeps a `last_seen` dict and jumps `l` directly past the duplicate.

**Optimal approach:**
- Dict `char → last index seen`.
- For each `r`, if `ch` was seen at an index ≥ `l`, move `l = last[ch]+1`.
- Update `last[ch]=r` and track `r-l+1`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">s="abcabcbb" — jump l past duplicates</text>
  <g font-family="monospace" font-size="14">
    <text x="80"  y="80" fill="#4A90D9">a</text>
    <text x="120" y="80" fill="#4A90D9">b</text>
    <text x="160" y="80" fill="#4A90D9">c</text>
    <text x="200" y="80" fill="#E74C3C">a*</text>
    <text x="240" y="80" fill="#4A90D9">b</text>
    <text x="280" y="80" fill="#4A90D9">c</text>
    <text x="320" y="80" fill="#E74C3C">b*</text>
    <text x="360" y="80" fill="#E74C3C">b*</text>
  </g>
  <text x="300" y="140" text-anchor="middle" font-size="13" fill="#27AE60">best window length = 3 (abc)</text>
</svg>

**Complexity:** Mine O(n) / O(k) → Optimal O(n) / O(k)

**Takeaway:** When shrinking, jump past the duplicate instead of removing one char at a time.
