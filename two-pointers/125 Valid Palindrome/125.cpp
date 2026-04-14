class Solution {
    public:
        bool isPalindrome(string s) {
            int left = 0;
            int right = s.size()-1;
    
            while (left < right){
                if (!isalnum(s[left])) {
                    left += 1;
                }
                else if (!isalnum(s[right])){
                    right -= 1;
                }
    
                else {
                    if (tolower(s[left]) == tolower(s[right])){
                        left += 1;
                        right -= 1;
                    }
                    else{
                        return false;
                    }
                }
            }
            return true;
        }
    };