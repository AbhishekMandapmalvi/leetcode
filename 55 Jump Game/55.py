class Solution:
    def canJump(self, nums: List[int]) -> bool:
        pos=len(nums)-1
        last_pos=pos

        for i in range(len(nums)-1,-1,-1):
            if i+nums[i]>=last_pos:
                last_pos=i

        return last_pos==0