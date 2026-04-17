import pygame
import os

class SoundManager:
    """Класс для управления звуками и музыкой"""
    
    def __init__(self, config):
        self.config = config
        self.sounds = {}
        self.music_playing = False
        self.sound_enabled = False
        
        # Проверяем, можем ли мы использовать звук
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.sound_enabled = True
            print("✅ Звуковая система инициализирована")
        except Exception as e:
            print(f"❌ Звуковая система недоступна: {e}")
            print("Игра будет работать без звука")
        
        # Загрузка звуков
        self.load_sounds()
    
    def load_sounds(self):
        """Загрузка звуковых эффектов"""
        if not self.sound_enabled:
            print("⚠️ Звук отключён, загрузка звуков пропущена")
            return
            
        sound_paths = self.config.settings.get('paths', {})
        
        # Загружаем звуки с ПРАВИЛЬНЫМИ расширениями из вашего config
        sounds_to_load = {
            'click': sound_paths.get('click_sound', ''),
            'capture': sound_paths.get('capture_sound', ''),
            'move': sound_paths.get('move_sound', '')
        }
        
        print("\n🔍 Загрузка звуковых эффектов:")
        for name, path in sounds_to_load.items():
            print(f"  {name} -> {path}")
            
            if path and os.path.exists(path):
                file_size = os.path.getsize(path)
                if file_size > 0:
                    try:
                        self.sounds[name] = pygame.mixer.Sound(path)
                        if 'sound' in self.config.settings:
                            volume = self.config.settings['sound'].get('effects_volume', 0.5)
                            self.sounds[name].set_volume(volume)
                        print(f"  ✅ {name}. Загружен ({file_size} байт)")
                    except Exception as e:
                        print(f"  ❌ {name}. Ошибка: {e}")
                        self.sounds[name] = None
                else:
                    print(f"  ⚠️ {name}. Файл пуст (0 байт)")
                    self.sounds[name] = None
            else:
                print(f"  ❌ {name}. Файл не найден: {path}")
                self.sounds[name] = None
        
        print()
    
    def play_sound(self, sound_name):
        """Воспроизведение звукового эффекта"""
        if not self.sound_enabled:
            return
            
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
                print(f"🔊 Воспроизведён звук: {sound_name}")
            except Exception as e:
                print(f"⚠️ Не удалось воспроизвести {sound_name}: {e}")
        else:
            if sound_name not in self.sounds:
                print(f"⚠️ Звук '{sound_name}' не найден в словаре")
    
    def play_music(self):
        """Воспроизведение фоновой музыки"""
        if not self.sound_enabled or self.music_playing:
            return
            
        music_path = self.config.settings['paths'].get('music', '')
        print(f"\n🎵 Загрузка музыки: {music_path}")
        
        if music_path and os.path.exists(music_path):
            file_size = os.path.getsize(music_path)
            if file_size > 0:
                try:
                    pygame.mixer.music.load(music_path)
                    if 'sound' in self.config.settings:
                        volume = self.config.settings['sound'].get('music_volume', 0.3)
                        pygame.mixer.music.set_volume(volume)
                        print(f"  Громкость музыки: {volume}")
                    pygame.mixer.music.play(-1)  # Бесконечное повторение
                    self.music_playing = True
                    print(f"✅ Музыка воспроизводится ({file_size} байт)")
                except Exception as e:
                    print(f"❌ Не удалось загрузить музыку: {e}")
            else:
                print(f"⚠️ Файл музыки пуст (0 байт)")
        else:
            print(f"❌ Файл музыки не найден: {music_path}")
    
    def stop_music(self):
        """Остановка фоновой музыки"""
        if not self.sound_enabled:
            return
            
        try:
            pygame.mixer.music.stop()
            self.music_playing = False
            print("🔇 Музыка остановлена")
        except:
            pass
    
    def set_music_volume(self, volume):
        """Установка громкости музыки"""
        if not self.sound_enabled:
            return
            
        try:
            if 'sound' not in self.config.settings:
                self.config.settings['sound'] = {}
            self.config.settings['sound']['music_volume'] = volume
            pygame.mixer.music.set_volume(volume)
            print(f"🎵 Громкость музыки: {volume}")
        except:
            pass
    
    def set_effects_volume(self, volume):
        """Установка громкости звуковых эффектов"""
        if not self.sound_enabled:
            return
            
        try:
            if 'sound' not in self.config.settings:
                self.config.settings['sound'] = {}
            self.config.settings['sound']['effects_volume'] = volume
            for name, sound in self.sounds.items():
                if sound:
                    sound.set_volume(volume)
            print(f"🔊 Громкость эффектов: {volume}")
        except:
            pass