import random
import numpy as np

class AIPlayer:
    def __init__(self):
        self.size = 15  # Board size is 15x15
        
    def get_move(self, board):
        """
        Get the next move for the AI player
        board: 2D list representing the game board (0 = empty, 1 = player 1, 2 = player 2)
        returns: (x, y) coordinates of the AI move
        """
        # Convert the board to numpy array for easier manipulation
        np_board = np.array(board)
        
        # If this is the first move or second move, place near the center
        total_moves = np.count_nonzero(np_board)
        if total_moves == 0:
            # First move - play at the center
            return (7, 7)
        
        if total_moves == 1:
            # Second move - play adjacent to the player's move
            player_x, player_y = np.where(np_board == 1)
            if len(player_x) > 0:
                px, py = player_x[0], player_y[0]
                moves = []
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size and np_board[nx, ny] == 0:
                        moves.append((nx, ny))
                if moves:
                    return random.choice(moves)
        
        # Defense first - check if player is about to win and block
        for i in range(self.size):
            for j in range(self.size):
                if np_board[i, j] == 0:  # Empty position
                    # Check if player would win by placing here
                    np_board[i, j] = 1
                    if self._check_win(np_board, j, i, 1):
                        np_board[i, j] = 0  # Restore the board
                        return (j, i)  # Block the player
                    np_board[i, j] = 0  # Restore the board
        
        # Offense - check if AI can win in the next move
        for i in range(self.size):
            for j in range(self.size):
                if np_board[i, j] == 0:  # Empty position
                    # Check if AI would win by placing here
                    np_board[i, j] = 2
                    if self._check_win(np_board, j, i, 2):
                        np_board[i, j] = 0  # Restore the board
                        return (j, i)  # Winning move
                    np_board[i, j] = 0  # Restore the board
        
        # Evaluate each empty position and choose the best
        best_score = -float('inf')
        best_move = None
        
        for i in range(self.size):
            for j in range(self.size):
                if np_board[i, j] == 0:  # Empty position
                    # Score this position
                    score = self._score_position(np_board, j, i)
                    if score > best_score:
                        best_score = score
                        best_move = (j, i)
        
        # If no good move found, choose a random empty cell
        if best_move is None:
            empty_positions = [(j, i) for i in range(self.size) for j in range(self.size) if np_board[i, j] == 0]
            if empty_positions:
                best_move = random.choice(empty_positions)
            else:
                # No empty positions left - should not happen
                return (0, 0)
        
        return best_move
    
    def _check_win(self, board, x, y, player):
        """Check if a move at (x, y) by player would win the game"""
        directions = [
            [(0, 1), (0, -1)],   # Vertical
            [(1, 0), (-1, 0)],   # Horizontal
            [(1, 1), (-1, -1)],  # Diagonal /
            [(1, -1), (-1, 1)]   # Diagonal \
        ]
        
        for dir_pair in directions:
            count = 1  # Count the piece we just placed
            
            # Check in both directions
            for dx, dy in dir_pair:
                nx, ny = x, y
                
                # Count consecutive pieces in this direction
                for _ in range(4):  # Need 4 more to make 5 in a row
                    nx, ny = nx + dx, ny + dy
                    if (0 <= nx < self.size and 0 <= ny < self.size and 
                        board[ny, nx] == player):
                        count += 1
                    else:
                        break
                
            if count >= 5:
                return True
        
        return False
    
    def _score_position(self, board, x, y, player=2):
        """
        Evaluate the score of placing at position (x, y)
        Higher score means better position
        """
        # Base score
        score = 0
        
        # Check all directions
        directions = [
            [(0, 1), (0, -1)],   # Vertical
            [(1, 0), (-1, 0)],   # Horizontal
            [(1, 1), (-1, -1)],  # Diagonal /
            [(1, -1), (-1, 1)]   # Diagonal \
        ]
        
        for dir_pair in directions:
            # Score for AI (player 2)
            ai_score = self._count_sequence(board, x, y, dir_pair, 2)
            score += ai_score * ai_score  # Square to prioritize longer sequences
            
            # Score for blocking player (player 1)
            player_score = self._count_sequence(board, x, y, dir_pair, 1)
            score += player_score * player_score * 0.9  # Slightly less weight for defense
        
        # Bonus for central positions (center control is strategically valuable)
        center_x, center_y = self.size // 2, self.size // 2
        distance_from_center = abs(x - center_x) + abs(y - center_y)
        score += max(0, (self.size - distance_from_center) / 2)
        
        return score
    
    def _count_sequence(self, board, x, y, dir_pair, player):
        """
        Count the potential sequence length in a direction if we place at (x, y)
        """
        max_count = 1  # The piece we would place
        open_ends = 0  # Number of open ends (good for future growth)
        
        # Temporarily place the piece
        board[y, x] = player
        
        # Check in both directions
        for dx, dy in dir_pair:
            count = 1  # Start with 1 for the piece at (x, y)
            nx, ny = x, y
            is_open_end = True
            
            # Count in this direction
            for _ in range(4):  # We need at most 4 more to make 5
                nx, ny = nx + dx, ny + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if board[ny, nx] == player:
                        count += 1
                    elif board[ny, nx] == 0:
                        # Open end
                        open_ends += 1
                        break
                    else:
                        # Blocked by opponent
                        is_open_end = False
                        break
                else:
                    # Out of bounds
                    is_open_end = False
                    break
            
            if is_open_end and count > max_count:
                max_count = count
        
        # Remove the temporary piece
        board[y, x] = 0
        
        # Adjust score based on open ends
        if open_ends == 2:
            max_count *= 1.5  # Two open ends is very good
        elif open_ends == 1:
            max_count *= 1.2  # One open end is good
        
        return max_count