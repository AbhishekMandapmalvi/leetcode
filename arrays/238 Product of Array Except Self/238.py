class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        n = len(nums)
        # Initialize result list with 1s, same length as input
        total = [1] * n

        # Initialize left product accumulator
        left = 1
        # First pass: Left to right
        for i in range(n):
            # Store the product of all elements to the left
            total[i] = left
            # Update left product for next iteration
            left *= nums[i]
        
        # Initialize right product accumulator
        right = 1
        # Second pass: Right to left
        for i in range(n-1, -1, -1):
            # Multiply stored left product with right product
            total[i] *= right
            # Update right product for next iteration
            right *= nums[i]
        
        # Return the result list
        return total
