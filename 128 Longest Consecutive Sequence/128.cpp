class Solution {
public:
    int longestConsecutive(vector<int>& nums) {
        unordered_map<int, int> hashmap;
        int max_len = 0;
        int curr_len = 0;

        for (int num : nums) {
            if (hashmap.find(num) == hashmap.end()) {
                int left = hashmap.find(num - 1) != hashmap.end() ? hashmap[num - 1] : 0;
                int right = hashmap.find(num + 1) != hashmap.end() ? hashmap[num + 1] : 0;

                curr_len = left + right + 1;
                hashmap[num] = curr_len;

                max_len = max(max_len, curr_len);

                if (left != 0) {
                    hashmap[num - left] = curr_len;
                }
                if (right != 0) {
                    hashmap[num + right] = curr_len;
                }
            }
        }
        return max_len;
    }
};