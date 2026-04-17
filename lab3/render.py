import pygame
import os

class Renderer:
    """Класс для отрисовки игровых объектов"""
    
    def __init__(self, screen, config):
        self.screen = screen
        self.config = config
        self.cell_size = config.get_cell_size()
        self.board_size = config.get_board_size()
        self.board_offset_x = (screen.get_width() - self.cell_size * self.board_size) // 2
        self.board_offset_y = (screen.get_height() - self.cell_size * self.board_size) // 2
        
        # Загрузка цветов
        self.light_color = pygame.Color(config.get_color('light_cell'))
        self.dark_color = pygame.Color(config.get_color('dark_cell'))
        self.highlight_color = pygame.Color(config.get_color('highlight'))
        self.possible_move_color = pygame.Color(config.get_color('possible_move'))
        
        # Загрузка изображений шашек
        self.piece_images = {}
        self.load_piece_images()

    def create_default_piece_images(self):
        """Создание изображений-заглушек для шашек"""
        size = self.cell_size - 10
        
        # Белая простая шашка
        white_man = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(white_man, (255, 255, 255), (size//2, size//2), size//2 - 2)
        pygame.draw.circle(white_man, (0, 0, 0), (size//2, size//2), size//2 - 2, 2)
        self.piece_images['white_man'] = white_man
        
        # Черная простая шашка
        black_man = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(black_man, (0, 0, 0), (size//2, size//2), size//2 - 2)
        pygame.draw.circle(black_man, (255, 255, 255), (size//2, size//2), size//2 - 2, 2)
        self.piece_images['black_man'] = black_man
        
        # Белая дамка (с короной)
        white_king = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(white_king, (255, 255, 255), (size//2, size//2), size//2 - 2)
        pygame.draw.circle(white_king, (255, 215, 0), (size//2, size//2), size//2 - 2, 3)
        crown_points = [
            (size//2 - 10, size//2 - 5),
            (size//2 - 5, size//2 - 10),
            (size//2, size//2 - 15),
            (size//2 + 5, size//2 - 10),
            (size//2 + 10, size//2 - 5)
        ]
        pygame.draw.polygon(white_king, (255, 215, 0), crown_points, 2)
        self.piece_images['white_king'] = white_king
        
        # Черная дамка (с короной)
        black_king = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(black_king, (0, 0, 0), (size//2, size//2), size//2 - 2)
        pygame.draw.circle(black_king, (255, 215, 0), (size//2, size//2), size//2 - 2, 3)
        pygame.draw.polygon(black_king, (255, 215, 0), crown_points, 2)
        self.piece_images['black_king'] = black_king
        
        print("Созданы изображения-заглушки для шашек")

    def load_piece_images(self):
        """Загрузка изображений шашек"""
        self.create_default_piece_images()
        
        piece_paths = self.config.game_config.get('pieces', {})
        
        for piece_type, path in piece_paths.items():
            try:
                if path and os.path.exists(path):
                    image = pygame.image.load(path)
                    image = pygame.transform.scale(image, (self.cell_size - 10, self.cell_size - 10))
                    self.piece_images[piece_type] = image
                    print(f"Загружено пользовательское изображение: {path}")
            except Exception as e:
                print(f"Не удалось загрузить изображение {path}: {e}")

    def draw_board(self, flip=False):
        """Отрисовка шахматной доски"""
        for row in range(self.board_size):
            for col in range(self.board_size):
                if flip:
                    draw_row = self.board_size - 1 - row
                    draw_col = self.board_size - 1 - col
                else:
                    draw_row = row
                    draw_col = col
                
                if (draw_row + draw_col) % 2 == 0:
                    color = self.light_color
                else:
                    color = self.dark_color
                
                x = self.board_offset_x + col * self.cell_size
                y = self.board_offset_y + row * self.cell_size
                pygame.draw.rect(self.screen, color, (x, y, self.cell_size, self.cell_size))

    def draw_piece(self, piece, flip=False):
        """Отрисовка одной шашки"""
        if piece.is_white():
            piece_type = 'white_king' if piece.is_king else 'white_man'
        else:
            piece_type = 'black_king' if piece.is_king else 'black_man'
        
        if flip:
            draw_row = self.board_size - 1 - piece.row
            draw_col = self.board_size - 1 - piece.col
        else:
            draw_row = piece.row
            draw_col = piece.col
        
        x = self.board_offset_x + draw_col * self.cell_size
        y = self.board_offset_y + draw_row * self.cell_size
        
        if piece_type in self.piece_images and self.piece_images[piece_type]:
            image = self.piece_images[piece_type]
            image_rect = image.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
            self.screen.blit(image, image_rect)
        
        if hasattr(piece, 'selected') and piece.selected:
            highlight_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
            pygame.draw.rect(self.screen, self.highlight_color, highlight_rect, 3)

    def draw_pieces(self, board, flip=False):
        """Отрисовка всех шашек"""
        for piece in board.pieces:
            self.draw_piece(piece, flip)

    def draw_possible_moves(self, board, flip=False):
        """Отрисовка возможных ходов для выбранной шашки"""
        if board.selected_piece:
            valid_moves = board.get_valid_moves(board.selected_piece)
            for row, col in valid_moves:
                if flip:
                    draw_row = self.board_size - 1 - row
                    draw_col = self.board_size - 1 - col
                else:
                    draw_row = row
                    draw_col = col
                
                x = self.board_offset_x + draw_col * self.cell_size
                y = self.board_offset_y + draw_row * self.cell_size
                s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                r, g, b = self.possible_move_color.r, self.possible_move_color.g, self.possible_move_color.b
                s.fill((r, g, b, 128))
                self.screen.blit(s, (x, y))

    def draw_animations(self, animation_manager):
        """Отрисовка всех анимаций"""
        if not animation_manager:
            return
        
        # Анимация движения
        move_anim = animation_manager.get_move_animation()
        if move_anim and not move_anim.is_finished() and move_anim.piece:
            pos = move_anim.get_render_position(
                self.cell_size, self.board_offset_x, self.board_offset_y
            )
            if move_anim.piece.is_white():
                piece_type = 'white_king' if move_anim.piece.is_king else 'white_man'
            else:
                piece_type = 'black_king' if move_anim.piece.is_king else 'black_man'
            
            if piece_type in self.piece_images:
                image = self.piece_images[piece_type]
                image_rect = image.get_rect(center=pos)
                self.screen.blit(image, image_rect)
        
        # Анимации смерти
        for death_anim in animation_manager.get_death_animations():
            if death_anim.piece:
                if death_anim.piece.is_white():
                    piece_type = 'white_king' if death_anim.piece.is_king else 'white_man'
                else:
                    piece_type = 'black_king' if death_anim.piece.is_king else 'black_man'
                
                if piece_type in self.piece_images:
                    death_anim.render(self.screen, self.piece_images[piece_type])
        
        # Анимации взятия (полёт)
        for capture_anim in animation_manager.get_capture_animations():
            if capture_anim.attacker:
                if capture_anim.attacker.is_white():
                    piece_type = 'white_king' if capture_anim.attacker.is_king else 'white_man'
                else:
                    piece_type = 'black_king' if capture_anim.attacker.is_king else 'black_man'
                
                if piece_type in self.piece_images:
                    capture_anim.render(self.screen, self.piece_images[piece_type])