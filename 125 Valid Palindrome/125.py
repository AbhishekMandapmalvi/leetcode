class Solution:
    def isPalindrome(self, s: str) -> bool:
        cleaned_string = ''.join(char for char in s if char.isalnum())
        lowercase_string = ""

        for char in cleaned_string:
            if "A" <= char <= "Z":
                lowercase_string += chr(ord(char)+32)
            else:
                lowercase_string += char
        
        start = 0
        end = len(lowercase_string)-1

        for i in range(len(lowercase_string)):
            if lowercase_string[i] != lowercase_string[end-i]:
                return False
        
        return True