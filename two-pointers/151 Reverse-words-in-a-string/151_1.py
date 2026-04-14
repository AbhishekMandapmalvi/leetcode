class Solution:
    def reverseWords(self, s: str) -> str:
        s=s.split(" ")
        s=s[::-1]
        i=0

        while i<len(s):
            if len(s[i])==0:
                s.pop(i)
            else:
                i+=1

        return " ".join(s)