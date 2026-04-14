class Solution {
public:
    bool isValidSudoku(vector<vector<char>>& board) {
        // Initialize hash sets for rows, columns, and 3x3 boxes
        unordered_map<int, unordered_set<char>> row_hash, col_hash, box_hash;

        // Iterate through each cell in the 9x9 Sudoku board
        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < 9; j++) {
                // Skip empty cells (denoted by '.')
                if (board[i][j] == '.') continue;

                // Calculate the index of the 3x3 box
                int box_index = (i / 3) * 3 + (j / 3);

                // Check if the current number already exists in the same row, column, or 3x3 box
                if (row_hash[i].count(board[i][j]) ||
                    col_hash[j].count(board[i][j]) ||
                    box_hash[box_index].count(board[i][j])) {
                    return false;  // If it exists, the Sudoku is invalid
                }

                // Add the current number to the respective hash sets
                box_hash[box_index].insert(board[i][j]);
                row_hash[i].insert(board[i][j]);
                col_hash[j].insert(board[i][j]);
            }
        }

        // If we've made it through all checks, the Sudoku is valid
        return true;
    }
};
