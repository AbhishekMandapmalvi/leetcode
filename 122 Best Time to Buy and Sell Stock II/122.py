class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        ans=0

        for f in range(1,len(prices)):
            if prices[f]>prices[f-1]:
                ans+=prices[f]-prices[f-1]
            
        return ans