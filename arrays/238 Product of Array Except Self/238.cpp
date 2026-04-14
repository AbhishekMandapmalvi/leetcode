class Solution {
public:
    vector<int> productExceptSelf(vector<int>& nums) {
        int n = nums.size();
        // Initialize result vector with 1s, same size as input
        vector<int> total(n, 1);

        // Initialize left and right product accumulators
        int left = 1;
        int right = 1;

        // First pass: Left to right
        for (int i = 0; i < n; i++) {
            // Store the product of all elements to the left
            total[i] = left;
            // Update left product for next iteration
            left *= nums[i];
        }

        // Second pass: Right to left
        for (int i = n - 1; i >= 0; i--) {
            // Multiply stored left product with right product
            total[i] *= right;
            // Update right product for next iteration
            right *= nums[i];
        }

        // Return the result vector
        return total;
    }
};
