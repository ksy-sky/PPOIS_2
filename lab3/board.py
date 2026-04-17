import pygame

class Piece:
    """Класс, представляющий шашку"""
    
    def __init__(self, color, row, col, is_king=False):
        self.color = color
        self.row = row
        self.col = col
        self.is_king = is_king
        self.selected = False
        self.image = None
        self.rect = None
        self.just_captured = False
        
    def get_position(self):
        return (self.row, self.col)
    
    def set_position(self, row, col):
        self.row = row
        self.col = col
    
    def make_king(self):
        self.is_king = True
    
    def is_white(self):
        return self.color == 'white'
    
    def is_black(self):
        return self.color == 'black'
    
    def __repr__(self):
        return f"Piece({self.color}, {self.row}, {self.col}, king={self.is_king})"


class Board:
    """Класс, представляющий игровую доску"""
    
    def __init__(self, config, on_player_switch=None):
        self.config = config
        self.board_size = config.get_board_size()
        self.cell_size = config.get_cell_size()
        self.pieces = []
        self.current_player = 'white'
        self.selected_piece = None
        self.must_capture = False
        self.capturing_piece = None
        self.on_player_switch = on_player_switch
        
        self.init_board()
    
    def init_board(self):
        """Инициализация начальной расстановки шашек"""
        self.pieces = []
        
        # Чёрные шашки (сверху, rows 0-2)
        for row in range(3):
            for col in range(self.board_size):
                if (row + col) % 2 == 1:
                    piece = Piece('black', row, col)
                    self.pieces.append(piece)
        
        # Белые шашки (снизу, rows 5-7)
        for row in range(self.board_size - 3, self.board_size):
            for col in range(self.board_size):
                if (row + col) % 2 == 1:
                    piece = Piece('white', row, col)
                    self.pieces.append(piece)
        
        print(f"Доска инициализирована: {len(self.pieces)} шашек")
    
    def get_piece_at(self, row, col):
        for piece in self.pieces:
            if piece.row == row and piece.col == col:
                return piece
        return None
    
    def remove_piece(self, piece):
        if piece in self.pieces:
            self.pieces.remove(piece)
            print(f"Шашка удалена: {piece}")
    
    def move_piece(self, piece, new_row, new_col):
        piece.set_position(new_row, new_col)
        
        if not piece.is_king:
            if (piece.is_white() and new_row == 0) or (piece.is_black() and new_row == self.board_size - 1):
                piece.make_king()
                print(f"Шашка превратилась в дамку на ({new_row}, {new_col})")
    
    def get_captures(self, piece, row, col):
        """Получить все возможные взятия для шашки"""
        captures = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            step = 1
            target = None
            
            while True:
                check_row = row + dr * step
                check_col = col + dc * step
                
                if not (0 <= check_row < self.board_size and 0 <= check_col < self.board_size):
                    break
                
                current = self.get_piece_at(check_row, check_col)
                
                if current:
                    if current.color != piece.color and target is None:
                        target = current
                        landing_step = step + 1
                        while True:
                            landing_row = row + dr * landing_step
                            landing_col = col + dc * landing_step
                            
                            if not (0 <= landing_row < self.board_size and 0 <= landing_col < self.board_size):
                                break
                            
                            if self.get_piece_at(landing_row, landing_col) is None:
                                captures.append({
                                    'target': target,
                                    'landing_row': landing_row,
                                    'landing_col': landing_col,
                                    'row_diff': dr,
                                    'col_diff': dc
                                })
                                break
                            else:
                                break
                        break
                    else:
                        break
                step += 1
        
        # Для обычных шашек (не дамок)
        if not piece.is_king:
            captures = []
            for dr, dc in directions:
                target_row = row + dr
                target_col = col + dc
                landing_row = row + dr * 2
                landing_col = col + dc * 2
                
                if (0 <= target_row < self.board_size and 
                    0 <= target_col < self.board_size and
                    0 <= landing_row < self.board_size and 
                    0 <= landing_col < self.board_size):
                    
                    target = self.get_piece_at(target_row, target_col)
                    landing = self.get_piece_at(landing_row, landing_col)
                    
                    if (target and target.color != piece.color and 
                        landing is None and (landing_row + landing_col) % 2 == 1):
                        captures.append({
                            'target': target,
                            'landing_row': landing_row,
                            'landing_col': landing_col,
                            'row_diff': dr,
                            'col_diff': dc
                        })
        
        return captures
    
    def get_all_captures(self, color):
        all_captures = []
        for piece in self.pieces:
            if piece.color == color:
                captures = self.get_captures(piece, piece.row, piece.col)
                if captures:
                    all_captures.append((piece, captures))
        return all_captures
    
    def has_captures(self, color):
        if self.capturing_piece:
            if self.capturing_piece.color == color:
                return len(self.get_captures(self.capturing_piece, 
                                             self.capturing_piece.row, 
                                             self.capturing_piece.col)) > 0
            return False
        
        return len(self.get_all_captures(color)) > 0
    
    def is_valid_move(self, piece, new_row, new_col):
        if (new_row + new_col) % 2 == 0:
            return False
        
        if self.get_piece_at(new_row, new_col) is not None:
            return False
        
        row_diff = new_row - piece.row
        col_diff = abs(new_col - piece.col)
        
        if self.has_captures(self.current_player):
            captures = self.get_captures(piece, piece.row, piece.col)
            for capture in captures:
                if capture['landing_row'] == new_row and capture['landing_col'] == new_col:
                    return True
            return False
        
        if not piece.is_king:
            if piece.is_white():
                direction = -1
            else:
                direction = 1
            
            if row_diff == direction and col_diff == 1:
                return True
            return False
        else:
            if abs(row_diff) == col_diff:
                return self.is_path_clear(piece.row, piece.col, new_row, new_col)
            return False
    
    def is_path_clear(self, from_row, from_col, to_row, to_col):
        row_step = 1 if to_row > from_row else -1
        col_step = 1 if to_col > from_col else -1
        
        current_row = from_row + row_step
        current_col = from_col + col_step
        
        while current_row != to_row and current_col != to_col:
            if self.get_piece_at(current_row, current_col) is not None:
                return False
            current_row += row_step
            current_col += col_step
        
        return True
    
    def execute_capture(self, piece, target, landing_row, landing_col):
        start_row, start_col = piece.row, piece.col
        captured_piece = target
        
        self.remove_piece(target)
        self.move_piece(piece, landing_row, landing_col)
        print(f"Взятие выполнено! {piece.color} бьёт на ({landing_row}, {landing_col})")
        
        further_captures = self.get_captures(piece, landing_row, landing_col)
        if further_captures:
            print(f"⚠️ Шашка может бить дальше! Доступно {len(further_captures)} взятий")
            self.capturing_piece = piece
            self.selected_piece = piece
            piece.selected = True
            return True, captured_piece, start_row, start_col, landing_row, landing_col
        else:
            print(f"✅ Взятия закончены")
            self.capturing_piece = None
            return True, captured_piece, start_row, start_col, landing_row, landing_col

    def make_move(self, piece, new_row, new_col):
        start_row, start_col = piece.row, piece.col
        
        captures = self.get_captures(piece, piece.row, piece.col)
        
        for capture in captures:
            if capture['landing_row'] == new_row and capture['landing_col'] == new_col:
                success, captured_piece, s_row, s_col, e_row, e_col = self.execute_capture(
                    piece, capture['target'], new_row, new_col
                )
                if not self.capturing_piece:
                    self.switch_player()
                return success, captured_piece, s_row, s_col, e_row, e_col
        
        if self.is_valid_move(piece, new_row, new_col):
            self.move_piece(piece, new_row, new_col)
            self.switch_player()
            return True, None, start_row, start_col, new_row, new_col
        
        return False, None, start_row, start_col, start_row, start_col

    def switch_player(self):
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        self.selected_piece = None
        self.capturing_piece = None
        print(f"Теперь ходят: {self.current_player}")
        
        if self.on_player_switch:
            self.on_player_switch()
        
        if self.has_captures(self.current_player):
            print(f"Внимание! У {self.current_player} есть обязательные взятия!")
    
    def get_valid_moves(self, piece):
        valid_moves = []
        
        if self.capturing_piece:
            if piece == self.capturing_piece:
                captures = self.get_captures(piece, piece.row, piece.col)
                for capture in captures:
                    valid_moves.append((capture['landing_row'], capture['landing_col']))
            return valid_moves
        
        if self.has_captures(self.current_player):
            captures = self.get_captures(piece, piece.row, piece.col)
            for capture in captures:
                valid_moves.append((capture['landing_row'], capture['landing_col']))
            return valid_moves
        
        if piece.is_king:
            for dr in (-1, 1):
                for dc in (-1, 1):
                    step = 1
                    while True:
                        new_row = piece.row + dr * step
                        new_col = piece.col + dc * step
                        
                        if not (0 <= new_row < self.board_size and 0 <= new_col < self.board_size):
                            break
                        
                        if (new_row + new_col) % 2 == 0:
                            step += 1
                            continue
                        
                        if self.get_piece_at(new_row, new_col) is not None:
                            break
                        
                        if self.is_valid_move(piece, new_row, new_col):
                            valid_moves.append((new_row, new_col))
                        else:
                            break
                        
                        step += 1
        else:
            if piece.is_white():
                directions = [(-1, -1), (-1, 1)]
            else:
                directions = [(1, -1), (1, 1)]
            
            for dr, dc in directions:
                new_row = piece.row + dr
                new_col = piece.col + dc
                
                if 0 <= new_row < self.board_size and 0 <= new_col < self.board_size:
                    if (new_row + new_col) % 2 == 1:
                        if self.is_valid_move(piece, new_row, new_col):
                            valid_moves.append((new_row, new_col))
        
        return valid_moves
    
    def get_valid_moves_for_player(self, color):
        moves = []
        for piece in self.pieces:
            if piece.color == color:
                moves.extend(self.get_valid_moves(piece))
        return moves
    
    def check_game_over(self):
        white_count = sum(1 for p in self.pieces if p.color == 'white')
        black_count = sum(1 for p in self.pieces if p.color == 'black')
        
        if white_count == 0:
            return 'black'
        if black_count == 0:
            return 'white'
        
        current_moves = self.get_valid_moves_for_player(self.current_player)
        if len(current_moves) == 0:
            return 'black' if self.current_player == 'white' else 'white'
        
        return None
    
    def calculate_score(self, player_color):
        my_score = 0
        opponent_score = 0
        
        for piece in self.pieces:
            if piece.color == player_color:
                my_score += 10
                if piece.is_king:
                    my_score += 20
            else:
                opponent_score += 10
                if piece.is_king:
                    opponent_score += 20
        
        return my_score + (opponent_score // 2)