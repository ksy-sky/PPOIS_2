import pygame

class MoveAnimation:
    """Анимация перемещения шашки"""
    
    def __init__(self, piece, start_row, start_col, end_row, end_col, duration=0.2):
        self.piece = piece
        self.start_pos = (start_row, start_col)
        self.end_pos = (end_row, end_col)
        self.duration = duration
        self.start_time = None
        self.finished = False
        self.progress = 0.0
        self.current_row = float(start_row)
        self.current_col = float(start_col)
    
    def start(self):
        self.start_time = pygame.time.get_ticks()
        self.finished = False
        self.progress = 0.0
        self.current_row = float(self.start_pos[0])
        self.current_col = float(self.start_pos[1])
    
    def tick(self):
        if self.start_time is None or self.finished:
            return self.progress
        
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000.0
        self.progress = min(elapsed / self.duration, 1.0)
        
        self.current_row = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * self.progress
        self.current_col = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * self.progress
        
        if self.progress >= 1.0:
            self.finished = True
        
        return self.progress

    def get_render_position(self, cell_size, offset_x, offset_y):
        x = offset_x + self.current_col * cell_size + cell_size // 2
        y = offset_y + self.current_row * cell_size + cell_size // 2
        return (int(x), int(y))
    
    def is_finished(self):
        return self.finished

class AnimationManager:
    """Менеджер для управления анимациями"""
    
    def __init__(self):
        self.active_move_animation = None
        self.active_death_animations = []
        self.active_capture_animations = []
    
    def start_move_animation(self, piece, start_row, start_col, end_row, end_col, duration=0.2):
        if piece is None:
            return None
        
        self.active_move_animation = MoveAnimation(
            piece, start_row, start_col, end_row, end_col, duration
        )
        self.active_move_animation.start()
        return self.active_move_animation
    
    def start_death_animation(self, piece, cell_size, offset_x, offset_y, duration=0.3):
        anim = DeathAnimation(piece, cell_size, offset_x, offset_y, duration)
        anim.start()
        self.active_death_animations.append(anim)
        return anim
    
    def start_capture_animation(self, attacker, target, start_row, start_col, end_row, end_col, 
                                cell_size, offset_x, offset_y, duration=0.2):
        anim = CaptureAnimation(attacker, target, start_row, start_col, end_row, end_col,
                                cell_size, offset_x, offset_y, duration)
        anim.start()
        self.active_capture_animations.append(anim)
        return anim
    
    def tick(self):
        if self.active_move_animation:
            self.active_move_animation.tick()
            if self.active_move_animation.is_finished():
                self.active_move_animation = None
        
        for anim in self.active_death_animations[:]:
            anim.tick()
            if anim.is_finished():
                self.active_death_animations.remove(anim)
        
        for anim in self.active_capture_animations[:]:
            anim.tick()
            if anim.is_finished():
                self.active_capture_animations.remove(anim)
    
    def is_animating(self):
        return (self.active_move_animation is not None and not self.active_move_animation.is_finished()) or \
               len(self.active_death_animations) > 0 or \
               len(self.active_capture_animations) > 0
    
    def get_move_animation(self):
        return self.active_move_animation
    
    def get_death_animations(self):
        return self.active_death_animations
    
    def get_capture_animations(self):
        return self.active_capture_animations
    
class DeathAnimation:
    """Анимация исчезновения шашки (смерть)"""
    
    def __init__(self, piece, cell_size, offset_x, offset_y, duration=0.3):
        self.piece = piece
        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.duration = duration
        self.start_time = None
        self.finished = False
        self.progress = 0.0
        self.scale = 1.0
        self.alpha = 255
    
    def start(self):
        self.start_time = pygame.time.get_ticks()
        self.finished = False
        self.progress = 0.0
        self.scale = 1.0
        self.alpha = 255
    
    def tick(self):
        if self.start_time is None or self.finished:
            return self.progress
        
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000.0
        self.progress = min(elapsed / self.duration, 1.0)
        
        self.scale = 1.0 - self.progress
        self.alpha = int(255 * (1.0 - self.progress))
        
        if self.progress >= 1.0:
            self.finished = True
        
        return self.progress
    
    def render(self, screen, piece_image):
        if self.finished:
            return
        
        x = self.offset_x + self.piece.col * self.cell_size + self.cell_size // 2
        y = self.offset_y + self.piece.row * self.cell_size + self.cell_size // 2
        
        if self.scale > 0:
            new_size = int(self.cell_size - 10) * self.scale
            if new_size > 0:
                scaled_image = pygame.transform.scale(piece_image, (int(new_size), int(new_size)))
                
                if self.alpha < 255:
                    scaled_image.set_alpha(self.alpha)
                
                rect = scaled_image.get_rect(center=(x, y))
                screen.blit(scaled_image, rect)
    
    def is_finished(self):
        return self.finished


class CaptureAnimation:
    """Анимация полёта шашки при взятии"""
    
    def __init__(self, attacker, target, start_row, start_col, end_row, end_col, cell_size, offset_x, offset_y, duration=0.2):
        self.attacker = attacker
        self.target = target
        self.start_row = start_row
        self.start_col = start_col
        self.end_row = end_row
        self.end_col = end_col
        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.duration = duration
        self.start_time = None
        self.finished = False
        self.progress = 0.0
        self.current_row = float(start_row)
        self.current_col = float(start_col)
        self.trail_particles = []
        self.rotation = 0.0
    
    def start(self):
        self.start_time = pygame.time.get_ticks()
        self.finished = False
        self.progress = 0.0
        self.current_row = float(self.start_row)
        self.current_col = float(self.start_col)
        self.rotation = 0.0
    
    def tick(self):
        if self.start_time is None or self.finished:
            return self.progress
        
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000.0
        self.progress = min(elapsed / self.duration, 1.0)
        
        self.current_row = self.start_row + (self.end_row - self.start_row) * self.progress
        self.current_col = self.start_col + (self.end_col - self.start_col) * self.progress
        
        self.rotation = 360 * self.progress
        
        if self.progress < 0.9 and self.progress > 0.1:
            self.trail_particles.append({
                'row': self.current_row,
                'col': self.current_col,
                'life': 0.3
            })
        
        for particle in self.trail_particles[:]:
            particle['life'] -= 0.05
            if particle['life'] <= 0:
                self.trail_particles.remove(particle)
        
        if self.progress >= 1.0:
            self.finished = True
        
        return self.progress
    
    def render(self, screen, attacker_image):
        if self.finished:
            return
        
        for particle in self.trail_particles:
            x = self.offset_x + particle['col'] * self.cell_size + self.cell_size // 2
            y = self.offset_y + particle['row'] * self.cell_size + self.cell_size // 2
            alpha = int(100 * (particle['life'] / 0.3))
            pygame.draw.circle(screen, (255, 200, 0, alpha), (int(x), int(y)), self.cell_size // 6)
        
        x = self.offset_x + self.current_col * self.cell_size + self.cell_size // 2
        y = self.offset_y + self.current_row * self.cell_size + self.cell_size // 2
        
        rotated_image = pygame.transform.rotate(attacker_image, self.rotation)
        rect = rotated_image.get_rect(center=(x, y))
        screen.blit(rotated_image, rect)
    
    def is_finished(self):
        return self.finished