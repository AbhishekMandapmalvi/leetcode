class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        if len(s)==0:
            return 0
        else:
            ans = []
            first=0
            second=first+1
            temp = [s[first]]
            
            while first<len(s):
                if second<len(s) and s[second] not in temp:
                    temp.append(s[second])
                    second+=1
                
                if second==len(s) or s[second] in temp:
                    ans.append(len(temp))
                    temp = []
                    first+=1
                    second=first+1
                    if first<len(s):
                        temp.append(s[first])
                    
            return max(ans)