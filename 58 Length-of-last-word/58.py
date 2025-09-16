class Solution:
    def lengthOfLastWord(self, s: str) -> int:
        i,cntr=len(s)-1,0

        while i>=0 and s[i]==" ":
            i-=1
        while i>=0 and s[i]!=" ":
            cntr+=1
            i-=1

        return cntr