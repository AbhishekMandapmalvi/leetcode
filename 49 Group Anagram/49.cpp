class Solution {
public:
    vector<vector<string>> groupAnagrams(vector<string>& strs) {
        // Initialize an unordered_map to store sorted strings as keys and their anagrams as values
        unordered_map<string, vector<string>> hash;

        // Iterate through each string in the input vector
        for (const string& s : strs) {
            // Create a copy of the string to sort
            string sorted_s = s;
            // Sort the characters of the current string
            sort(sorted_s.begin(), sorted_s.end());

            // Add the original string to the vector of anagrams for this sorted string
            hash[sorted_s].push_back(s);
        }

        // Initialize a vector to store the final result
        vector<vector<string>> result;

        // Iterate through the hash map and add each group of anagrams to the result
        for (const auto& pair : hash) {
            result.push_back(pair.second);
        }

        // Return the result vector containing groups of anagrams
        return result;
    }
};