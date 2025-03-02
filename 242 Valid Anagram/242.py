class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        # Initialize two dictionaries to store the frequency of characters in both strings
        string1 = {}
        string2 = {}
        
        # If the lengths of the two strings are different, they cannot be anagrams
        if len(s) != len(t):
            return False

        # Count the frequency of each character in string `s`
        for i in s:
            if i not in string1:  # If the character is not already in the dictionary
                string1[i] = 1   # Add it with a count of 1
            else:
                string1[i] += 1  # Otherwise, increment its count
        
        # Count the frequency of each character in string `t`
        for i in t:
            if i not in string2:  # If the character is not already in the dictionary
                string2[i] = 1   # Add it with a count of 1
            else:
                string2[i] += 1  # Otherwise, increment its count
        
        # Compare the two dictionaries; if they are equal, `s` and `t` are anagrams
        return string1 == string2
