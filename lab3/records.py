import yaml
import os
from datetime import datetime

class RecordsManager:
    """Класс для управления таблицей рекордов (только лучший рекорд)"""
    
    def __init__(self, config):
        self.config = config
        self.records_file = config.game_config.get('game', {}).get('records_file', 'records.yaml')
        self.records = self.load_records()
    
    def load_records(self):
        """Загрузка рекордов из файла"""
        try:
            if os.path.exists(self.records_file):
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'records' in data:
                        return data['records']
        except Exception as e:
            print(f"Ошибка загрузки рекордов: {e}")
        return []
    
    def save_records(self):
        """Сохранение рекордов в файл"""
        try:
            data = {'records': self.records}
            with open(self.records_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            print(f"Рекорды сохранены в {self.records_file}")
        except Exception as e:
            print(f"Ошибка сохранения рекордов: {e}")
    
    def add_record(self, player_name, score, game_date=None):
        """Добавление нового рекорда (сохраняем только лучший)"""
        if game_date is None:
            game_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        record = {
            'name': player_name,
            'score': score,
            'date': game_date
        }
        
        # Добавляем новый рекорд
        self.records.append(record)
        # Сортируем по убыванию счёта
        self.records.sort(key=lambda x: x['score'], reverse=True)
        # Оставляем ТОЛЬКО ПЕРВЫЙ (лучший) рекорд
        self.records = self.records[:1]
        self.save_records()
    
    def is_new_record(self, score):
        """Проверка, является ли счёт новым рекордом (лучше текущего лучшего)"""
        # Если нет ни одного рекорда — да
        if len(self.records) == 0:
            return True
        # Если счёт БОЛЬШЕ текущего лучшего — да
        return score > self.records[0]['score']

    def get_top_record(self):
        """Получение лучшего рекорда"""
        if self.records:
            return self.records[0]
        return None
    
    def get_records(self):
        """Получение всех рекордов (только лучший)"""
        return self.records