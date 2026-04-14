class Solution {
public:
    bool isAnagram(string s, string t) {
        // If the lengths of the two strings are not equal, they can't be anagrams
        if (s.length() != t.length()) {
            return false;
        }

        // Create two hash maps to count the frequency of characters in both strings
        unordered_map<char, int> string1;
        unordered_map<char, int> string2;

        // Count the frequency of each character in string `s`
        for (char c : s) {
            string1[c]++;
        }

        // Count the frequency of each character in string `t`
        for (char c : t) {
            string2[c]++;
        }

        // Compare the two maps; if they are equal, `s` and `t` are anagrams
        return string1 == string2;
    }
};
