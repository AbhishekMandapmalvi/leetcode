class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Initialize a hash map (dictionary) to store numbers we've seen and their indices
        hash = {}

        # Iterate through the list with both index (`i`) and value (`num`)
        for i, num in enumerate(nums):
            # Calculate the complement (remaining value needed to reach the target)
            rem = target - num

            # Check if the complement is already in the hash map
            if rem in hash:
                # If found, return the indices of the current number and its complement
                return [hash[rem], i]

            # Otherwise, store the current number and its index in the hash map
            hash[num] = i