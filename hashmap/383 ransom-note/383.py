class Solution:
    def canConstruct(self, ransomNote: str, magazine: str) -> bool:
        hm={}

        for i in magazine:
            if i not in hm:
                hm[i]=1
            else:
                hm[i]+=1
        
        for i in ransomNote:
            if i not in hm or hm[i]==0:
                return False
            else:
                hm[i]-=1

        return True