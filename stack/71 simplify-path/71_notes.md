# #71 — Simplify Path

> **Difficulty:** Medium | **Patterns:** Stack, String | **Date:** 2026-04-13

**My approach:** Split on `/`, push dir names, pop on `..`, skip `.` and empty.

**Where I went off track:** Nothing.

**Optimal approach:**
- `path.split("/")` → parts.
- For each part: skip empty/`.`; pop on `..`; else push.
- Return `"/" + "/".join(stack)`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">"/a/./b/../../c/" → "/c"</text>
  <g font-family="monospace" font-size="13">
    <text x="60" y="70" fill="#4A90D9">a push → [a]</text>
    <text x="60" y="95" fill="#4A90D9">. skip → [a]</text>
    <text x="60" y="120" fill="#4A90D9">b push → [a,b]</text>
    <text x="300" y="70" fill="#E74C3C">.. pop → [a]</text>
    <text x="300" y="95" fill="#E74C3C">.. pop → []</text>
    <text x="300" y="120" fill="#27AE60">c push → [c]</text>
  </g>
</svg>

**Complexity:** Mine O(n) / O(n) → Optimal same

**Takeaway:** Path simplification is a textbook stack problem — always split first, then walk.
