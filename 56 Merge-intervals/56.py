class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        intervals=sorted(intervals)
        result=[intervals[0]]

        for i in range(1,len(intervals)):
            
            if intervals[i][0]<=result[-1][1] and intervals[i][1]>result[-1][1]:
                result[-1][1]=intervals[i][1]
            
            elif intervals[i][0]<=result[-1][1] and intervals[i][1]<=result[-1][1]:
                pass
            
            else:
                result.append(intervals[i])
        
        return result