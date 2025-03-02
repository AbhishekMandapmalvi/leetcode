class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        // Create an unordered_map (hash table) to store the numbers we've seen and their indices
        unordered_map<int, int> hash;

        // Iterate through the array to find the two numbers that add up to the target
        for (int i = 0; i < nums.size(); i++) {
            // Calculate the complement (remaining value needed to reach the target)
            int rem = target - nums[i];

            // Check if the complement is already in the hash table
            if (hash.find(rem) != hash.end()) {
                // If found, return the indices of the current number and its complement
                return { hash[rem], i };
            }

            // Otherwise, store the current number and its index in the hash table
            hash[nums[i]] = i;
        }

        // If no solution is found, return an empty vector (this case won't occur as per problem constraints)
        return {};
    }
};