class Solution:
    def isIsomorphic(self, s: str, t: str) -> bool:
        if len(s)!=len(t):
            return False

        s_t={}
        t_s={}
        
        for char_s,char_t in zip(s,t):
            if char_s not in s_t and char_t not in t_s:
                s_t[char_s]=char_t
                t_s[char_t]=char_s
            
            elif s_t.get(char_s)!=char_t or t_s.get(char_t)!=char_s:
                return False

        return True