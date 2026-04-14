# #20 — Valid Parentheses

> **Difficulty:** Easy | **Patterns:** Stack, String | **Date:** 2026-04-13

**My approach:** Stack + closer→opener dict.

**Where I went off track:** Minor — left a `print(ls)` debug statement inside the loop. Remove it. Also the odd-length early return is nice but not strictly necessary.

**Optimal approach:**
- Dict `closer → opener`.
- Push openers; on closer, pop and compare.
- Return `stack is empty`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">"({[]})" — push, push, push, pop, pop, pop ✓</text>
  <g font-family="monospace" font-size="14">
    <rect x="150" y="60" width="40" height="30" fill="#4A90D9"/><text x="170" y="80" text-anchor="middle" fill="white">(</text>
    <rect x="150" y="90" width="40" height="30" fill="#4A90D9"/><text x="170" y="110" text-anchor="middle" fill="white">{</text>
    <rect x="150" y="120" width="40" height="30" fill="#4A90D9"/><text x="170" y="140" text-anchor="middle" fill="white">[</text>
    <text x="280" y="110" fill="#27AE60">pop on ] { )</text>
  </g>
</svg>

**Complexity:** Mine O(n) / O(n) → Optimal O(n) / O(n)

**Takeaway:** Delete debug prints before committing — they slow the code and clutter output.
