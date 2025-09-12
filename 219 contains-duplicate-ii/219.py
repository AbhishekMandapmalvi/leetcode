class Solution:
    def containsNearbyDuplicate(self, nums: List[int], k: int) -> bool:
        hs={}

        for i in range(len(nums)):
            if nums[i] not in hs:
                hs[nums[i]]=i
            elif nums[i] in hs and abs(hs[nums[i]]-i)<=k:
                return True
            else:
                hs[nums[i]]=i

        return False