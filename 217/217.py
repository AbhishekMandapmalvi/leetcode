class Solution:
    def containsDuplicate(self, nums: List[int]) -> bool:
        # Initialize an empty dictionary to keep track of the elements we've seen
        a = {}
        
        # Create a set from the input list `nums` (not used in the logic here, so this line can be removed)
        unique_set = set(nums)
        
        # Iterate through each number in the list `nums`
        for j in nums:
            # Check if the current number `j` is not already in the dictionary `a`
            if j not in a:
                # If it's not in the dictionary, add it with a value of 1
                a[j] = 1
            else:
                # If the number is already in the dictionary, it means we found a duplicate
                return True
        
        # If no duplicates are found after iterating through the entire list, return False
        return False
