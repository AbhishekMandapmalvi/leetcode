class Solution {
public:
    bool containsDuplicate(vector<int>& nums) {
        unordered_set<int> seen; // To store unique numbers

        for (int num : nums) {
            if (seen.find(num) != seen.end()) { // If the number is already in the set
                return true;
            }
            seen.insert(num); // Add the number to the set
        }

        return false; // No duplicates found
    }
};