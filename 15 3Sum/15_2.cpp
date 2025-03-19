class Solution {
    public:
        vector<vector<int>> threeSum(vector<int>& nums) {
            sort(begin(nums),end(nums));
            vector<vector<int>> ans;
            int n = nums.size();
            
            for (int first = 0; first < n; ++first) {
                if (nums[first]>0) break;
                if (first > 0 && nums[first] == nums[first-1]) continue;
    
                int second=first+1;
                int last=n-1;
    
                while (second<last){
                    int sum = nums[first]+nums[second]+nums[last];
                    
                    if (sum<0) ++second;
                    else if (sum>0) --last;
                    else {
                        ans.push_back({nums[first],nums[second],nums[last]});
                    
                        while (second < last && nums[second] == nums[second+1]) ++second;
                        while (second < last && nums[last] == nums[last-1]) --last;
                        ++second;
                        --last;
                    }
                }
            }
            return ans;
        }
    };