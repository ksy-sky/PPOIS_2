import pygame
import sys
import socket
import json
import threading
import time
from queue import Queue
from config import config
from menu import Menu
from sounds import SoundManager
from board import Board, Piece
from render import Renderer
from records import RecordsManager
from animations import AnimationManager

class OnlineClient:
    def __init__(self, game):
        self.game = game
        self.socket = None
        self.connected = False
        self.my_color = None
        self.messages = Queue()
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('localhost', 5555))
            self.socket.setblocking(False)
            self.connected = True
            
            def receive():
                buffer = ""
                while self.connected:
                    try:
                        data = self.socket.recv(4096).decode()
                        if data:
                            buffer += data
                            while '\n' in buffer:
                                line, buffer = buffer.split('\n', 1)
                                if line:
                                    msg = json.loads(line)
                                    self.messages.put(msg)
                    except BlockingIOError:
                        time.sleep(0.01)
                    except:
                        break
            
            threading.Thread(target=receive, daemon=True).start()
            time.sleep(0.1)
            return True
        except:
            return False
    
    def send(self, msg):
        if self.connected:
            try:
                self.socket.send((json.dumps(msg) + '\n').encode())
            except:
                pass
    
    def update(self):
        while not self.messages.empty():
            msg = self.messages.get()
            if msg['type'] == 'color':
                self.my_color = msg['color']
                print(f"Мой цвет: {self.my_color}")
            elif msg['type'] == 'start':
                print("СТАРТ!")
                self.game.start_online_game(self.my_color)
            elif msg['type'] == 'move':
                print(f"Ход соперника: {msg['move']}")
                self.game.apply_opponent_move(msg['move'])
    
    def send_move(self, move):
        self.send({'type': 'move', 'move': move})

class Game:
    def __init__(self):
        pygame.init()
        
        self.screen_width = config.get_screen_width()
        self.screen_height = config.get_screen_height()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Шашки")
         
        self.clock = pygame.time.Clock()
        self.fps = config.settings['fps']
        self.running = True
        self.current_state = "menu"
        
        self.sound_manager = SoundManager(config)
        self.menu = Menu(self.screen)
        self.records_manager = RecordsManager(config)
        self.animation_manager = AnimationManager()
        
        self.board = None
        self.renderer = None
        self.flip_board = False
        self.local_flip_enabled = False
        self.game_over = False
        self.winner = None
        self.temp_score = 0
        self.input_name = ""
        
        self.local_player_color = 'white'
        
        self.online = None
        self.is_online = False
        self.my_color = None
        
        self.sound_manager.play_music()
    
    def start_local_game(self):
        """Локальная игра - доска переворачивается после каждого хода"""
        self.is_online = False
        self.local_player_color = None
        self.local_flip_enabled = True
        
        self.board = Board(config, on_player_switch=self.on_local_player_switched)
        self.renderer = Renderer(self.screen, config)
        self.current_state = "game"
        self.flip_board = False
        self.game_over = False
        self.winner = None
        
        print("Локальная игра начата! Доска будет переворачиваться после каждого хода")
    
    def start_online_game(self, color):
        """Онлайн игра - доска НЕ переворачивается после ходов"""
        self.is_online = True
        self.my_color = color
        self.local_player_color = color
        self.local_flip_enabled = False
        
        self.board = Board(config, on_player_switch=None)
        self.renderer = Renderer(self.screen, config)
        self.current_state = "game"
        self.game_over = False
        self.winner = None
        
        self.flip_board = (color == 'black')
        
        print(f"Онлайн игра начата! Вы играете {color}")
        print(f"Переворот доски: {self.flip_board} (фиксирован)")
    
    def on_local_player_switched(self):
        """Callback при смене игрока в локальной игре"""
        if self.local_flip_enabled and not self.is_online:
            self.flip_board = not self.flip_board
            print(f"🔄 Доска перевёрнута: {'чёрные снизу' if self.flip_board else 'белые снизу'}")
    
    def apply_opponent_move(self, move):
        """Применение хода соперника с правильной анимацией на перевёрнутой доске"""
        if self.game_over:
            return
        
        start_row, start_col, end_row, end_col = move
        
        # Для анимации используем преобразованные координаты (как видит игрок)
        if self.flip_board:
            anim_start = (7 - start_row, 7 - start_col)
            anim_end = (7 - end_row, 7 - end_col)
        else:
            anim_start = (start_row, start_col)
            anim_end = (end_row, end_col)
        
        # Логическая шашка (для изменения состояния игры)
        piece = self.board.get_piece_at(start_row, start_col)
        
        if not piece:
            print(f"Ошибка: шашка не найдена на логических координатах ({start_row}, {start_col})")
            return
        
        print(f"📥 Получен ход: логические ({start_row},{start_col}) -> ({end_row},{end_col})")
        print(f"📺 Анимация: ({anim_start[0]},{anim_start[1]}) -> ({anim_end[0]},{anim_end[1]})")
        
        # Применяем ход к логической доске
        success, captured, s_row, s_col, e_row, e_col = self.board.make_move(piece, end_row, end_col)
        
        if success:
            # Создаём временную копию шашки для анимации в правильном месте
            anim_piece = Piece(piece.color, anim_start[0], anim_start[1], piece.is_king)
            
            self.animation_manager.start_move_animation(
                anim_piece, 
                anim_start[0], anim_start[1],
                anim_end[0], anim_end[1],
                0.2
            )
            
            if captured:
                # Позиция захваченной шашки на экране
                if self.flip_board:
                    captured_pos = (7 - captured.row, 7 - captured.col)
                else:
                    captured_pos = (captured.row, captured.col)
                
                # Создаём временную копию для анимации смерти
                anim_captured = Piece(captured.color, captured_pos[0], captured_pos[1], captured.is_king)
                
                self.animation_manager.start_death_animation(
                    anim_captured, self.renderer.cell_size,
                    self.renderer.board_offset_x, self.renderer.board_offset_y, 0.3
                )
                
                self.animation_manager.start_capture_animation(
                    anim_piece, anim_captured,
                    anim_start[0], anim_start[1],
                    anim_end[0], anim_end[1],
                    self.renderer.cell_size, self.renderer.board_offset_x,
                    self.renderer.board_offset_y, 0.2
                )
            
            print(f"Ход соперника применён")
            
            if self.board.capturing_piece:
                self.board.selected_piece = self.board.capturing_piece
                self.board.selected_piece.selected = True
            
            self.check_game_end()
    
    def handle_click(self, row, col):
        """Обработка клика"""
        if self.game_over:
            return
        
        # Преобразование координат для отображения
        if self.flip_board:
            logic_row = 7 - row
            logic_col = 7 - col
        else:
            logic_row = row
            logic_col = col
        
        clicked = self.board.get_piece_at(logic_row, logic_col)
        
        # Если есть активная последовательность взятий
        if self.board.capturing_piece:
            piece = self.board.capturing_piece
            
            captures = self.board.get_captures(piece, piece.row, piece.col)
            for capture in captures:
                if capture['landing_row'] == logic_row and capture['landing_col'] == logic_col:
                    success, captured, s_row, s_col, e_row, e_col = self.board.make_move(piece, logic_row, logic_col)
                    
                    if success:
                        self.sound_manager.play_sound('capture')
                        
                        # Для анимации используем экранные координаты
                        if self.flip_board:
                            anim_start = (7 - s_row, 7 - s_col)
                            anim_end = (7 - e_row, 7 - e_col)
                        else:
                            anim_start = (s_row, s_col)
                            anim_end = (e_row, e_col)
                        
                        anim_piece = Piece(piece.color, anim_start[0], anim_start[1], piece.is_king)
                        
                        self.animation_manager.start_move_animation(
                            anim_piece, anim_start[0], anim_start[1], anim_end[0], anim_end[1], 0.2
                        )
                        
                        if captured:
                            if self.flip_board:
                                captured_pos = (7 - captured.row, 7 - captured.col)
                            else:
                                captured_pos = (captured.row, captured.col)
                            
                            anim_captured = Piece(captured.color, captured_pos[0], captured_pos[1], captured.is_king)
                            
                            self.animation_manager.start_death_animation(
                                anim_captured, self.renderer.cell_size,
                                self.renderer.board_offset_x, self.renderer.board_offset_y, 0.3
                            )
                            self.animation_manager.start_capture_animation(
                                anim_piece, anim_captured,
                                anim_start[0], anim_start[1], anim_end[0], anim_end[1],
                                self.renderer.cell_size, self.renderer.board_offset_x,
                                self.renderer.board_offset_y, 0.2
                            )
                        
                        if self.is_online:
                            self.online.send_move([s_row, s_col, e_row, e_col])
                        
                        if not self.board.capturing_piece:
                            self.board.selected_piece = None
                        
                        self.check_game_end()
                    return
            
            self.board.selected_piece = None
            self.board.capturing_piece = None
            return
        
        # Обычный выбор шашки
        if self.board.selected_piece is None:
            if clicked and clicked.color == self.board.current_player:
                if not self.is_online or (self.is_online and clicked.color == self.my_color):
                    self.board.selected_piece = clicked
                    clicked.selected = True
                    self.sound_manager.play_sound('click')
        else:
            piece = self.board.selected_piece
            success, captured, sr, sc, er, ec = self.board.make_move(piece, logic_row, logic_col)
            
            if success:
                self.sound_manager.play_sound('capture' if captured else 'move')
                
                # Для анимации используем экранные координаты
                if self.flip_board:
                    anim_start = (7 - sr, 7 - sc)
                    anim_end = (7 - er, 7 - ec)
                else:
                    anim_start = (sr, sc)
                    anim_end = (er, ec)
                
                anim_piece = Piece(piece.color, anim_start[0], anim_start[1], piece.is_king)
                
                self.animation_manager.start_move_animation(
                    anim_piece, anim_start[0], anim_start[1], anim_end[0], anim_end[1], 0.2
                )
                
                if captured:
                    if self.flip_board:
                        captured_pos = (7 - captured.row, 7 - captured.col)
                    else:
                        captured_pos = (captured.row, captured.col)
                    
                    anim_captured = Piece(captured.color, captured_pos[0], captured_pos[1], captured.is_king)
                    
                    self.animation_manager.start_death_animation(
                        anim_captured, self.renderer.cell_size,
                        self.renderer.board_offset_x, self.renderer.board_offset_y, 0.3
                    )
                    self.animation_manager.start_capture_animation(
                        anim_piece, anim_captured,
                        anim_start[0], anim_start[1], anim_end[0], anim_end[1],
                        self.renderer.cell_size, self.renderer.board_offset_x,
                        self.renderer.board_offset_y, 0.2
                    )
                
                piece.selected = False
                self.board.selected_piece = None
                
                if self.is_online:
                    self.online.send_move([sr, sc, er, ec])
                    print(f"Ход отправлен: [{sr},{sc}] -> [{er},{ec}]")
                
                self.check_game_end()
            else:
                piece.selected = False
                self.board.selected_piece = None
    
    def check_game_end(self):
        """Проверка окончания игры"""
        winner = self.board.check_game_over()
        if winner:
            self.game_over = True
            self.winner = winner
            self.temp_score = self.board.calculate_score(winner)
            
            if not self.is_online:
                if self.records_manager.is_new_record(self.temp_score):
                    print(f"🎉 ПОБЕДИЛИ { 'БЕЛЫЕ' if winner == 'white' else 'ЧЁРНЫЕ' }! Новый рекорд! Счёт: {self.temp_score}")
                    self.current_state = "input_name"
                else:
                    top = self.records_manager.get_top_record()
                    print(f"🎉 ПОБЕДИЛИ { 'БЕЛЫЕ' if winner == 'white' else 'ЧЁРНЫЕ' }! Счёт: {self.temp_score}")
                    print(f"Рекорд не побит (текущий: {top['score'] if top else 0})")
                    self.current_state = "menu"
            else:
                if winner == self.local_player_color:
                    if self.records_manager.is_new_record(self.temp_score):
                        print(f"🎉 Вы победили! Новый рекорд! Счёт: {self.temp_score}")
                        self.current_state = "input_name"
                    else:
                        print(f"🎉 Вы победили! Счёт: {self.temp_score}")
                        self.current_state = "menu"
                else:
                    print(f"😢 Вы проиграли! Победили {winner}")
                    self.current_state = "game_over"
            
            self.sound_manager.play_sound('capture')
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif self.current_state == "menu":
                choice = self.menu.handle_event(event)
                if choice == "local":
                    self.start_local_game()
                elif choice == "online":
                    self.online = OnlineClient(self)
                    if self.online.connect():
                        self.current_state = "online_waiting"
                elif choice == "records":
                    self.current_state = "records"
                elif choice == "help":
                    self.current_state = "help"
                elif choice == "exit":
                    self.running = False
            
            elif self.current_state == "game":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.is_online and self.online:
                            self.online.connected = False
                        self.current_state = "menu"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.renderer:
                        mx, my = event.pos
                        cx = (mx - self.renderer.board_offset_x) // self.renderer.cell_size
                        cy = (my - self.renderer.board_offset_y) // self.renderer.cell_size
                        
                        if 0 <= cx < 8 and 0 <= cy < 8 and (cy + cx) % 2 == 1:
                            self.handle_click(cy, cx)
            
            elif self.current_state == "game_over":
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.current_state = "menu"
            
            elif self.current_state == "records":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.current_state = "menu"
            
            elif self.current_state == "help":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.current_state = "menu"
            
            elif self.current_state == "input_name":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        name = self.input_name.strip() or "Аноним"
                        self.records_manager.add_record(name, self.temp_score)
                        self.current_state = "menu"
                        self.input_name = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_name = self.input_name[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        self.current_state = "menu"
                        self.input_name = ""
                    elif len(self.input_name) < 20 and event.unicode.isprintable():
                        self.input_name += event.unicode
            
            elif self.current_state == "online_waiting":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.online:
                        self.online.connected = False
                    self.current_state = "menu"
    
    def update(self):
        if self.online:
            self.online.update()
        if self.current_state == "game":
            self.animation_manager.tick()
    
    def render(self):
        if self.current_state == "menu":
            self.menu.render()
        
        elif self.current_state == "game":
            self.screen.fill((0, 0, 0))
            if self.board and self.renderer:
                self.renderer.draw_board(flip=self.flip_board)
                self.renderer.draw_pieces(self.board, flip=self.flip_board)
                if self.board.selected_piece:
                    self.renderer.draw_possible_moves(self.board, flip=self.flip_board)
                self.renderer.draw_animations(self.animation_manager)
        
        elif self.current_state == "game_over":
            self.screen.fill((0, 0, 0))
            if self.board and self.renderer:
                self.renderer.draw_board(flip=self.flip_board)
                self.renderer.draw_pieces(self.board, flip=self.flip_board)
                self.renderer.draw_animations(self.animation_manager)
            self.render_game_over()
        
        elif self.current_state == "records":
            self.render_records()
        
        elif self.current_state == "help":
            self.render_help()
        
        elif self.current_state == "input_name":
            self.render_input_name()
        
        elif self.current_state == "online_waiting":
            self.render_online_waiting()
        
        pygame.display.flip()
    
    def render_game_over(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 80)
        small = pygame.font.Font(None, 52)
        
        if self.is_online:
            player_won = (self.winner == self.local_player_color)
        else:
            player_won = True
        
        if player_won:
            winner_text = "ВЫ ПОБЕДИЛИ!"
            color = (255, 215, 0)
        else:
            winner_text = f"ПОБЕДИЛИ { 'БЕЛЫЕ' if self.winner == 'white' else 'ЧЁРНЫЕ' }!"
            color = (255, 100, 100)
        
        text = font.render(winner_text, True, color)
        rect = text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
        self.screen.blit(text, rect)
        
        score_text = small.render(f"Счёт: {self.temp_score} очков", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 30))
        self.screen.blit(score_text, score_rect)
        
        if not player_won and self.is_online:
            hint = small.render("Нажмите любую клавишу для выхода в меню", True, (150, 150, 150))
            hint_rect = hint.get_rect(center=(self.screen_width//2, self.screen_height - 80))
            self.screen.blit(hint, hint_rect)
    
    def render_records(self):
        self.screen.fill((20, 30, 50))
        font = pygame.font.Font(None, 48)
        small = pygame.font.Font(None, 36)
        
        title = font.render("ТАБЛИЦА РЕКОРДОВ", True, (255, 215, 0))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 60))
        
        records = self.records_manager.get_records()
        y = 150
        
        if not records:
            text = small.render("Пока нет рекордов", True, (200, 200, 200))
            self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, y))
        else:
            for i, r in enumerate(records[:10]):
                text = small.render(f"{i+1}. {r['name']} - {r['score']} очков ({r['date']})", True, (255, 255, 255))
                self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, y))
                y += 45
        
        hint = small.render("ESC - назад", True, (150, 150, 150))
        self.screen.blit(hint, (self.screen_width//2 - hint.get_width()//2, self.screen_height - 50))
    
    def render_help(self):
        self.screen.fill((20, 30, 50))
        font = pygame.font.Font(None, 48)
        small = pygame.font.Font(None, 28)
        
        title = font.render("ПРАВИЛА ИГРЫ", True, (255, 215, 0))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 50))
        
        rules = [
            "1. Шашки ходят по диагонали на одну клетку вперёд",
            "2. Дамка ходит на любое количество клеток по диагонали",
            "3. Если есть возможность взять шашку - это обязательно!",
            "4. При достижении последней горизонтали - дамка",
            "5. Игрок без ходов или без шашек - проигрывает",
            "",
            "УПРАВЛЕНИЕ:",
            "• Клик по шашке - выбрать",
            "• Клик по клетке - сделать ход",
            "• ESC - выход в меню",
            "",
            "ОНЛАЙН РЕЖИМ:",
            "• Белые видят доску нормально",
            "• Чёрные видят доску перевёрнутой",
            "• Ход переключается автоматически",
            "",
            "ЛОКАЛЬНЫЙ РЕЖИМ:",
            "• Доска переворачивается после каждого хода",
            "• Играйте по очереди за одним компьютером"
        ]
        
        y = 120
        for rule in rules:
            if rule == "":
                y += 15
                continue
            text = small.render(rule, True, (255, 255, 255))
            self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, y))
            y += 32
        
        hint = small.render("ESC - назад", True, (150, 150, 150))
        self.screen.blit(hint, (self.screen_width//2 - hint.get_width()//2, self.screen_height - 50))
    
    def render_input_name(self):
        self.screen.fill((20, 30, 50))
        font = pygame.font.Font(None, 48)
        small = pygame.font.Font(None, 36)
        
        title = font.render("НОВЫЙ РЕКОРД!", True, (255, 215, 0))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 100))
        
        score = small.render(f"Ваш счёт: {self.temp_score} очков", True, (255, 255, 255))
        self.screen.blit(score, (self.screen_width//2 - score.get_width()//2, 180))
        
        prompt = small.render("Введите ваше имя:", True, (255, 255, 255))
        self.screen.blit(prompt, (self.screen_width//2 - prompt.get_width()//2, 280))
        
        box = pygame.Rect(self.screen_width//2 - 200, 330, 400, 50)
        pygame.draw.rect(self.screen, (60, 60, 80), box)
        pygame.draw.rect(self.screen, (255, 215, 0), box, 3)
        
        cursor = "|" if pygame.time.get_ticks() % 1000 < 500 else ""
        name_text = small.render(self.input_name + cursor, True, (255, 255, 255))
        self.screen.blit(name_text, (box.x + 10, box.y + 10))
        
        hint = small.render("ENTER - сохранить, ESC - отмена", True, (150, 150, 150))
        self.screen.blit(hint, (self.screen_width//2 - hint.get_width()//2, self.screen_height - 50))
    
    def render_online_waiting(self):
        self.screen.fill((20, 30, 50))
        font = pygame.font.Font(None, 48)
        small = pygame.font.Font(None, 32)
        
        text = font.render("Ожидание соперника...", True, (255, 215, 0))
        self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, self.screen_height//2 - 50))
        
        dots = "." * ((pygame.time.get_ticks() // 500) % 4)
        wait = small.render(f"Подключение{dots}", True, (200, 200, 200))
        self.screen.blit(wait, (self.screen_width//2 - wait.get_width()//2, self.screen_height//2 + 20))
        
        hint = small.render("ESC - отмена", True, (150, 150, 150))
        self.screen.blit(hint, (self.screen_width//2 - hint.get_width()//2, self.screen_height - 50))
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)
        
        if self.online:
            self.online.connected = False
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()