class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        # Initialize hash sets for rows, columns, and 3x3 boxes
        row_hash = {i: set() for i in range(9)}
        col_hash = {j: set() for j in range(9)}
        box_hash = {k: set() for k in range(9)}
        
        # Iterate through each cell in the 9x9 Sudoku board
        for i in range(9):
            for j in range(9):
                # Skip empty cells (denoted by '.')
                if board[i][j] == ".":
                    continue
                else:
                    # Calculate the index of the 3x3 box
                    box_index = (i // 3) * 3 + (j // 3)

                    # Check if the current number already exists in the same row, column, or 3x3 box
                    if (board[i][j] in row_hash[i] or 
                        board[i][j] in col_hash[j] or 
                        board[i][j] in box_hash[box_index]):
                        return False  # If it exists, the Sudoku is invalid

                    # Add the current number to the respective hash sets
                    box_hash[box_index].add(board[i][j])
                    row_hash[i].add(board[i][j])
                    col_hash[j].add(board[i][j])
        
        # If we've made it through all checks, the Sudoku is valid
        return True

