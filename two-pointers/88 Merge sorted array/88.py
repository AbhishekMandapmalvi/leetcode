class Solution:
    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
        """
        Do not return anything, modify nums1 in-place instead.
        """
        for i in range(m,len(nums1)):
            nums1[i]=nums2[i-m]
        
        curr=m
        prev=m-1

        while curr<len(nums1):
            if nums1[curr]<nums1[prev] and prev>-1:
                temp = nums1[curr]
                nums1[curr]=nums1[prev]
                nums1[prev]=temp

                curr-=1
                prev-=1
            
            else:
                curr+=1
                prev+=1