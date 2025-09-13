class Solution:
    def get_next(self,n: int) -> int:
            total_sum=0
            
            while n>0:
                n,digit=divmod(n,10)
                total_sum+=digit**2
                
            return total_sum
        
    def isHappy(self, n: int) -> bool:
        if 1<n<3:
            return False 
        
        seen=set()

        while n!=1 and n not in seen:
            seen.add(n)
            n=self.get_next(n)
        
        return n==1