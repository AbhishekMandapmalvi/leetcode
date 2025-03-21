class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        if s=="":
            return 0
        else:
            ans = []
            temp = []
            first=0
            second=first+1
            
            while first<len(s):
                temp.append(s[first])
                while (second<len(s)) and (s[second] not in temp):
                    temp.append(s[second])
                    second+=1
                
                ans.append(len(temp))
                temp = []
                first+=1
                second=first+1
            
            return max(ans)