class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        # If there's only one number in the list, return it
        if len(nums) == 1:
            return nums
        else:
            # Create a frequency map using Counter
            freq_map = Counter(nums)
            
            # Initialize a min heap
            min_heap = []
            
            # Iterate through each number and its frequency in the frequency map
            for num, freq in freq_map.items():
                # Push the (frequency, number) pair onto the min heap
                # We use frequency as the first element because heapq sorts based on the first element
                heapq.heappush(min_heap, (freq, num))

                # If the heap size exceeds k, remove the smallest element
                # This maintains the k most frequent elements in the heap
                if len(min_heap) > k:
                    heapq.heappop(min_heap)
            
            # Return a list of the k most frequent numbers
            # We only need the numbers, not their frequencies
            return [num for freq, num in min_heap]

