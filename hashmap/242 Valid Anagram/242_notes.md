# #242 — Valid Anagram

> **Difficulty:** Easy | **Patterns:** HashMap, String | **Date:** 2026-04-13

**My approach:** Two frequency dicts, compare equality.

**Where I went off track:** Not wrong, just verbose. Single `Counter(s)` then decrement as you walk `t` is tighter; for lowercase-only input, a size-26 int array is even leaner.

**Optimal approach:**
- Length check first.
- Build counter from `s`.
- Walk `t`, decrement; fail if any count goes negative.
- If you survive, it's a valid anagram.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">s="anagram" t="nagaram"</text>
  <g font-family="monospace" font-size="13">
    <text x="60" y="70" fill="#4A90D9">count(s): a:3 n:1 g:1 r:1 m:1</text>
    <text x="60" y="100" fill="#4A90D9">walk t: n--, a--, g--, a--, r--, a--, m--</text>
    <text x="60" y="130" fill="#27AE60">all zero → True</text>
  </g>
</svg>

**Complexity:** Mine O(n) / O(k) → Optimal O(n) / O(1) with fixed alphabet

**Takeaway:** One counter + negative-check is leaner than two counters + equality.
