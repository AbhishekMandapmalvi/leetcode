class Solution:
    def simplifyPath(self, path: str) -> str:
        ans=["/"]
        path=path.split("/")
        i=0

        while i<len(path):
            if path[i]==".":
                pass
            elif len(path[i])==0:
                pass
            elif path[i]=="..":
                if len(ans)>1:
                    ans.pop()
                    ans.pop()
            else:
                ans.append(path[i])
                if path[i]!="." or path[i]!=".." or path[i]!="/":
                    ans.append("/")
            i+=1
        
        if len(ans)>1:
            ans.pop()
        
        return "".join(ans)