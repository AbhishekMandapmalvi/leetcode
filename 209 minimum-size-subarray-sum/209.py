class Solution:
    def minSubArrayLen(self, target: int, nums: List[int]) -> int:
        left=0
        right=0
        summ=0
        ans=float('inf')

        for right in range(0, len(nums)):
            summ+=nums[right]
            
            while summ>=target:
                ans=min(ans, right-left+1)
                summ-=nums[left]
                left+=1
                
        return ans if ans != float('inf') else 0