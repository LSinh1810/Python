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
        try:
            # Convert the board to numpy array for easier manipulation
            np_board = np.array(board)
            
            # Nếu đây là nước đi đầu tiên, đặt ở trung tâm hoặc gần trung tâm
            total_moves = np.count_nonzero(np_board)
            if total_moves == 0:
                center_moves = [(7,7), (6,6), (6,7), (6,8), (7,6), (7,8), (8,6), (8,7), (8,8)]
                return random.choice(center_moves)
            
            # Kiểm tra nước đi chiến thắng ngay lập tức cho AI
            for i in range(self.size):
                for j in range(self.size):
                    if np_board[i, j] == 0:
                        np_board[i, j] = 2
                        if self._check_win(np_board, j, i, 2):
                            np_board[i, j] = 0
                            return (j, i)
                        np_board[i, j] = 0
            
            # Chặn nước đi chiến thắng và các nước đi nguy hiểm của người chơi
            for i in range(self.size):
                for j in range(self.size):
                    if np_board[i, j] == 0:
                        # Kiểm tra nước đi chiến thắng của người chơi
                        np_board[i, j] = 1
                        if self._check_win(np_board, j, i, 1):
                            np_board[i, j] = 0
                            return (j, i)
                        
                        # Kiểm tra các nước đi nguy hiểm
                        threat_score = self._evaluate_threat(np_board, j, i, 1)
                        if threat_score >= 1000:
                            np_board[i, j] = 0
                            return (j, i)
                            
                        np_board[i, j] = 0
            
            # Tìm nước đi tấn công tốt nhất
            best_score = -float('inf')
            best_moves = []
            
            valid_moves = self._get_valid_moves(np_board)
            
            if not valid_moves:
                empty_cells = [(j, i) for i in range(self.size) for j in range(self.size) if np_board[i, j] == 0]
                if empty_cells:
                    return random.choice(empty_cells)
                return (0, 0)
            
            # Đánh giá từng nước đi hợp lệ với trọng số khác nhau
            for x, y in valid_moves:
                np_board[y, x] = 2
                attack_score = self._evaluate_position(np_board, x, y, 2) * 1.2  # Tăng trọng số tấn công
                defense_score = self._evaluate_threat(np_board, x, y, 1) * 1.8   # Tăng trọng số phòng thủ
                position_score = self._evaluate_position_quality(x, y) * 1.5      # Đánh giá chất lượng vị trí
                total_score = attack_score + defense_score + position_score
                np_board[y, x] = 0
                
                if total_score > best_score:
                    best_score = total_score
                    best_moves = [(x, y)]
                elif total_score == best_score:
                    best_moves.append((x, y))
            
            if best_moves:
                # Chọn ngẫu nhiên từ các nước đi tốt nhất để tăng tính không thể đoán trước
                return random.choice(best_moves)
            
            # Nếu không tìm được nước đi tốt, chọn ngẫu nhiên từ các nước đi hợp lệ
            return random.choice(valid_moves)
            
        except Exception as e:
            print(f"Error in AI get_move: {str(e)}")
            empty_cells = [(j, i) for i in range(self.size) for j in range(self.size) if board[i][j] == 0]
            if empty_cells:
                return random.choice(empty_cells)
            return (0, 0)
    
    def _check_win(self, board, x, y, player):
        """Check if a move at (x, y) by player would win the game"""
        directions = [
            [(0, 1), (0, -1)],   # Vertical
            [(1, 0), (-1, 0)],   # Horizontal
            [(1, 1), (-1, -1)],  # Diagonal /
            [(1, -1), (-1, 1)]   # Diagonal \
        ]
        
        for dir_pair in directions:
            count = 1
            
            for dx, dy in dir_pair:
                nx, ny = x, y
                
                for _ in range(4):
                    nx, ny = nx + dx, ny + dy
                    if (0 <= nx < self.size and 0 <= ny < self.size and 
                        board[ny, nx] == player):
                        count += 1
                    else:
                        break
                
            if count >= 5:
                return True
        
        return False
    
    def _get_valid_moves(self, board):
        """Get list of valid moves (empty cells adjacent to existing pieces)"""
        valid_moves = []
        for i in range(self.size):
            for j in range(self.size):
                if board[i, j] != 0:
                    for di in [-2, -1, 0, 1, 2]:
                        for dj in [-2, -1, 0, 1, 2]:
                            if di == 0 and dj == 0:
                                continue
                            
                            ni, nj = i + di, j + dj
                            if (0 <= ni < self.size and 0 <= nj < self.size and 
                                board[ni, nj] == 0 and (nj, ni) not in valid_moves):
                                valid_moves.append((nj, ni))
        
        if not valid_moves and np.count_nonzero(board) > 0:
            center = self.size // 2
            for di in range(-3, 4):
                for dj in range(-3, 4):
                    ni, nj = center + di, center + dj
                    if (0 <= ni < self.size and 0 <= nj < self.size and board[ni, nj] == 0):
                        return [(nj, ni)]
        
        return valid_moves
    
    def _evaluate_position(self, board, x, y, player):
        """Evaluate the value of a position for a player"""
        score = 0
        opponent = 1 if player == 2 else 2
        
        directions = [
            [(0, 1), (0, -1)],   # Vertical
            [(1, 0), (-1, 0)],   # Horizontal
            [(1, 1), (-1, -1)],  # Diagonal /
            [(1, -1), (-1, 1)]   # Diagonal \
        ]
        
        for dir_pair in directions:
            my_count = 1
            opponent_count = 0
            empty_count = 0
            
            for dx, dy in dir_pair:
                for step in range(1, 5):
                    nx, ny = x + dx * step, y + dy * step
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        if board[ny, nx] == player:
                            my_count += 1
                        elif board[ny, nx] == 0:
                            empty_count += 1
                            break
                        else:
                            opponent_count += 1
                            break
                    else:
                        break
            
            if opponent_count == 0:
                if my_count >= 5:
                    score += 200000  # Tăng điểm cho nước thắng
                elif my_count == 4:
                    score += 20000   # Tăng điểm cho 4 quân
                elif my_count == 3:
                    score += 2000    # Tăng điểm cho 3 quân
                elif my_count == 2:
                    score += 200     # Tăng điểm cho 2 quân
            elif opponent_count == 1:
                if my_count >= 4:
                    score += 2000
                elif my_count == 3:
                    score += 200
                elif my_count == 2:
                    score += 20
        
        center = self.size // 2
        distance_from_center = abs(x - center) + abs(y - center)
        score += (self.size - distance_from_center) * 3  # Tăng ưu tiên vị trí trung tâm
        
        return score

    def _evaluate_threat(self, board, x, y, player):
        """Đánh giá mức độ nguy hiểm của một vị trí cho người chơi"""
        score = 0
        directions = [
            [(0, 1), (0, -1)],   # Vertical
            [(1, 0), (-1, 0)],   # Horizontal
            [(1, 1), (-1, -1)],  # Diagonal /
            [(1, -1), (-1, 1)]   # Diagonal \
        ]
        
        for dir_pair in directions:
            player_count = 1
            empty_before = 0
            empty_after = 0
            
            for dx, dy in dir_pair:
                nx, ny = x, y
                for step in range(1, 5):
                    nx, ny = nx + dx, ny + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        if board[ny, nx] == player:
                            player_count += 1
                        elif board[ny, nx] == 0:
                            if step == 1:
                                empty_before += 1
                            else:
                                empty_after += 1
                            break
                        else:
                            break
                    else:
                        break
            
            if player_count >= 4 and (empty_before > 0 or empty_after > 0):
                score += 10000  # Tăng điểm cho đe dọa chiến thắng
            elif player_count == 3 and empty_before > 0 and empty_after > 0:
                score += 2000   # Tăng điểm cho khả năng tạo thành 4 quân
            elif player_count == 2 and empty_before > 0 and empty_after > 0:
                score += 200    # Tăng điểm cho khả năng tạo thành 3 quân
        
        return score
        
    def _evaluate_position_quality(self, x, y):
        """Đánh giá chất lượng của một vị trí dựa trên các yếu tố chiến thuật"""
        score = 0
        center = self.size // 2
        
        # Ưu tiên các vị trí gần trung tâm
        distance = abs(x - center) + abs(y - center)
        score += (self.size - distance) * 5
        
        # Ưu tiên các vị trí tạo thành hình mẫu chiến thuật
        if 3 <= x <= 11 and 3 <= y <= 11:
            score += 100  # Khu vực chiến lược
            
        # Ưu tiên các góc phần tư
        if (x < center and y < center) or \
           (x < center and y > center) or \
           (x > center and y < center) or \
           (x > center and y > center):
            score += 50
            
        return score