class Solution:
    def longestConsecutive(self, nums):
        table = {}
        max_len = 0

        for num in nums:
            if num not in table:
                left = table.get(num-1, 0)
                right = table.get(num+1, 0)

                curr_len = left + right + 1
                table[num] = curr_len

                max_len = max(curr_len, max_len)
                
                if left != 0: 
                    table[num - left] = curr_len
                    
                if right != 0:
                    table[num + right] = curr_len
                    
        return max_len