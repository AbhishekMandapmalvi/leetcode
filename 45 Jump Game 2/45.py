class Solution:
    def jump(self, nums: List[int]) -> int:
        jumps,n=0,len(nums)
        end,farthest=0,0

        for i in range(n-1):
            farthest=max(farthest,nums[i]+i)

            if i==end:
                jumps+=1
                end=farthest

        return jumps