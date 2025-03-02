class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        # Initialize an empty dictionary to store sorted strings as keys and their anagrams as values
        hash = {}
        # Initialize an empty list to store the final result (not used in this implementation)
        result = []

        # Iterate through each string in the input list
        for i in strs:
            # Sort the characters of the current string and join them back into a string
            sorted_i = "".join(sorted(i))
            
            # If the sorted string is not in the hash dictionary
            if sorted_i not in hash:
                # Add it as a key with a list containing the original string as its value
                hash[sorted_i] = [i]
            else:
                # If the sorted string is already in the hash, append the original string to its list of anagrams
                hash[sorted_i].append(i)

        # Return the values of the hash dictionary as a list, which gives us groups of anagrams
        return list(hash.values())