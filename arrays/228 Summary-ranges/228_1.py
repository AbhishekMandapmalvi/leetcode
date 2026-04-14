class Solution:
    def summaryRanges(self, nums: List[int]) -> List[str]:
        if not nums:
            return []
        
        result = []
        start = nums  # Track actual values, not indices
        
        for i in range(1, len(nums)):
            # Check if current number breaks the sequence
            if nums[i] != nums[i-1] + 1:
                # Close current range and start new one
                if start == nums[i-1]:
                    result.append(str(start))
                else:
                    result.append(f"{start}->{nums[i-1]}")
                start = nums[i]  # Start new range
        
        # Handle the final range (no duplication needed)
        if start == nums[-1]:
            result.append(str(start))
        else:
            result.append(f"{start}->{nums[-1]}")
        
        return result
