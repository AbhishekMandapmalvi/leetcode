class Solution {
public:
    int lengthOfLongestSubstring(string s) {
        if (s.empty()) return 0;

        int maxLength = 0;
        int left = 0;  // Left pointer of the sliding window
        unordered_set<char> temp;  // Set for storing unique characters

        for (int right = 0; right < s.size(); ++right) {
            // Move left pointer until no duplicates in the window
            while (temp.count(s[right])) {
                temp.erase(s[left]);
                left++;
            }

            // Add current character to the set
            temp.insert(s[right]);

            // Update max length
            maxLength = max(maxLength, right - left + 1);
        }

        return maxLength;
    }
};