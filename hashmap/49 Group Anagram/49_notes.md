# #49 — Group Anagrams

> **Difficulty:** Medium | **Patterns:** HashMap, String | **Date:** 2026-04-13

**My approach:** Sort each string, use sorted string as dict key.

**Where I went off track:** Not wrong — and you even left an unused `result = []`. The tighter version uses a 26-int count tuple as the key (`O(k)` per string vs `O(k log k)` for sort).

**Optimal approach:**
- `defaultdict(list)`.
- For each string, build a length-26 count array → tuple → dict key.
- Return `groups.values()`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">["eat","tea","tan","ate","nat","bat"]</text>
  <g font-family="monospace" font-size="13">
    <text x="60" y="70" fill="#4A90D9">count("eat") = (1,0,...,1,0,...,1,..) → key</text>
    <text x="60" y="100" fill="#4A90D9">same key for eat/tea/ate</text>
    <text x="60" y="130" fill="#27AE60">→ [[eat,tea,ate],[tan,nat],[bat]]</text>
  </g>
</svg>

**Complexity:** Mine O(n·k log k) / O(n·k) → Optimal O(n·k) / O(n·k)

**Takeaway:** When the alphabet is small, a count tuple beats sorting as a hash key.
