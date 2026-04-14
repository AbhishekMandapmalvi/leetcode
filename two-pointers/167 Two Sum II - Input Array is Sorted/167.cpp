class Solution {
    public:
        vector<int> twoSum(vector<int>& numbers, int target) {
            int left = 0;
            int right = size(numbers)-1;
            vector<int> ans;
    
            while (left<right){
                int sum = numbers[left] + numbers[right];
                if (sum > target){
                    right-=1;
                }
                else if (sum < target){
                    left+=1;
                }
                else {
                    ans.push_back(left+1); 
                    ans.push_back(right+1);
                    return ans;
                }
            }
            return ans;
        }
    };