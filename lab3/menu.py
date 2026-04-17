import pygame
import random

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.w = screen.get_width()
        self.h = screen.get_height()
        
        self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 72)
        
        self.items = [
            "Локальная игра",
            "Онлайн игра",
            "Таблица рекордов",
            "Справка",
            "Выход"
        ]
        self.selected = 0
        
        self.background = self.create_bg()
    
    def create_bg(self):
        bg = pygame.Surface((self.w, self.h))
        for y in range(self.h):
            t = y / self.h
            r = int(40 * (1 - t) + 20 * t)
            g = int(20 * (1 - t) + 30 * t)
            b = int(60 * (1 - t) + 50 * t)
            pygame.draw.line(bg, (r, g, b), (0, y), (self.w, y))
        
        for _ in range(100):
            x = random.randint(0, self.w)
            y = random.randint(0, self.h)
            pygame.draw.circle(bg, (180, 180, 220), (x, y), random.randint(1, 2))
        
        return bg
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.items)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.items)
            elif event.key == pygame.K_RETURN:
                return self.get_action()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            start_y = 280
            for i, item in enumerate(self.items):
                y = start_y + i * 65
                text = self.font.render(item, True, (255,255,255))
                rect = text.get_rect(center=(self.w//2, y))
                if rect.collidepoint(mx, my):
                    self.selected = i
                    return self.get_action()
        return None
    
    def get_action(self):
        actions = ["local", "online", "records", "help", "exit"]
        return actions[self.selected]
    
    def render(self):
        self.screen.blit(self.background, (0, 0))
        
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))
        
        title = self.title_font.render("ШАШКИ", True, (255, 215, 0))
        self.screen.blit(title, (self.w//2 - title.get_width()//2, 120))
        
        start_y = 280
        for i, item in enumerate(self.items):
            y = start_y + i * 65
            
            if i == self.selected:
                rect = pygame.Rect(self.w//2 - 200, y - 25, 400, 50)
                pygame.draw.rect(self.screen, (255,255,255,60), rect, 2)
                color = (255, 255, 255)
            else:
                color = (160, 160, 160)
            
            text = self.font.render(item, True, color)
            self.screen.blit(text, (self.w//2 - text.get_width()//2, y - text.get_height()//2))