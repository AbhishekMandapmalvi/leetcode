class Solution:
    def simplifyPath(self, path: str) -> str:
        stack=[]
        path=path.split("/")
        
        for word in path:
            if word and word!="." and word!="..":
                stack.append(word)
            elif stack and word=="..":
                stack.pop()
        
        return "/"+"/".join(stack)