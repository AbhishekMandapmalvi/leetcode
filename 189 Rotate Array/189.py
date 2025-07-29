class Solution:
    def rotate(self, nums: List[int], k: int) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        nums1=nums[len(nums)-k%len(nums):len(nums)]
        nums2=nums[0:len(nums)-k%len(nums)]
        nums[0:k]=nums1
        nums[k:len(nums)]=nums2