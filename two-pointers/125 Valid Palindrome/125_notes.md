# #125 — Valid Palindrome

> **Difficulty:** Easy | **Patterns:** Two Pointers, String | **Date:** 2026-04-13

**My approach:** First attempt (125.py) built a cleaned+lowercased copy then compared ends. Second attempt (125_2.py) went straight to in-place two pointers.

**Where I went off track:** First solution used O(n) extra space and built the lowercase string manually with `chr(ord(...)+32)` — use `.lower()`. Second solution is the right answer.

**Optimal approach:**
- `l=0`, `r=n-1`.
- Skip non-alphanumerics on either side.
- Compare lowercased chars; fail fast on mismatch.
- No extra buffer.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">"A man, a plan, a canal: Panama"</text>
  <g font-family="monospace" font-size="14" fill="#2C3E50">
    <text x="30" y="80">A</text><text x="55" y="80" fill="#E74C3C">,</text>
    <text x="80" y="80">m</text><text x="105" y="80">a</text>
    <text x="130" y="80">n</text><text x="155" y="80" fill="#E74C3C">,</text>
    <text x="180" y="80">a</text><text x="205" y="80">...</text>
    <text x="380" y="80">c</text><text x="405" y="80">a</text>
    <text x="430" y="80">n</text><text x="455" y="80">a</text>
    <text x="480" y="80">l</text><text x="505" y="80" fill="#E74C3C">:</text>
    <text x="530" y="80">P</text><text x="555" y="80">...</text>
  </g>
  <g font-family="sans-serif" font-size="12">
    <text x="30" y="110" fill="#4A90D9">L→</text>
    <text x="530" y="110" fill="#4A90D9">←R</text>
    <text x="300" y="140" text-anchor="middle" fill="#27AE60">skip punctuation, compare a==a, m==m, ...</text>
  </g>
</svg>

**Complexity:** Mine O(n) / O(n) (first) or O(1) (second) → Optimal O(n) / O(1)

**Takeaway:** Reach for in-place two pointers before you reach for a cleaned copy.
