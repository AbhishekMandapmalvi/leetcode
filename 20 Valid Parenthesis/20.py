class Solution:
    def isValid(self, s: str) -> bool:
        if len(s)%2 != 0:
            return False
        else:       
            stack = {")":"(", "]":"[","}":"{"}
            ls = []

            for i in s:
                print(ls)
                if i not in stack.keys():
                    ls.append(i)
                elif i in stack.keys() and len(ls) > 0:
                    last_element = ls[len(ls)-1]
                    if last_element == stack[i]:
                        ls.pop(len(ls)-1)
                    else:
                        return False

            return len(ls)==0