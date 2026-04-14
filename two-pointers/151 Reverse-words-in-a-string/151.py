class Solution:
    def reverseWords(self, s: str) -> str:
        s=s.strip()
        return " ".join(s.split()[::-1])