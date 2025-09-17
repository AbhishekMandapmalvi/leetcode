class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        intervals=sorted(intervals)
        result=[intervals[0]]

        for i in range(1,len(intervals)):
            print(result,intervals)
            if intervals[i][0]<=intervals[i-1][1] and intervals[i][1]>intervals[i-1][1]:
                result.pop()
                result.append([intervals[i-1][0],intervals[i][1]])
            elif intervals[i][0]<=intervals[i-1][1] and intervals[i][1]<=intervals[i-1][1]:
                result.pop()
                result.append([intervals[i-1][0],intervals[i-1][1]])
            else:
                result.append(intervals[i])
        
        return result