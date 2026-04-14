class Solution:
    def wordPattern(self, pattern: str, s: str) -> bool:
        if len(pattern) != len(s.split()):
            return False
        
        s=s.split(" ")
        pattern=list(pattern)
        s_p={}
        p_s={}

        for i in range(len(pattern)):
            char, word = pattern[i], s[i]

            if char not in p_s and word not in s_p:
                p_s[char]=word
                s_p[word]=char

            else:
                if p_s.get(pattern[i]) != s[i] or s_p.get(s[i]) != pattern[i]:
                    return False
        
        return True