class Solution {
public:
    vector<int> topKFrequent(vector<int>& nums, int k) {
        // If there's only one number in the vector, return it
        if (nums.size() == 1) {
            return nums;
        }
        else {
            // Create a frequency map
            unordered_map<int, int> freq_map;
            for (int num : nums) {
                freq_map[num]++;
            }

            // Define a min heap
            // We use greater<> to create a min heap instead of the default max heap
            priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> min_heap;

            // Iterate through each number and its frequency in the frequency map
            for (auto& [num, freq] : freq_map) {
                // Push the (frequency, number) pair onto the min heap
                min_heap.push({ freq, num });

                // If the heap size exceeds k, remove the smallest element
                // This maintains the k most frequent elements in the heap
                if (min_heap.size() > k) {
                    min_heap.pop();
                }
            }

            // Create a vector to store the k most frequent numbers
            vector<int> result;
            while (!min_heap.empty()) {
                result.push_back(min_heap.top().second);
                min_heap.pop();
            }

            return result;
        }
    }
};
