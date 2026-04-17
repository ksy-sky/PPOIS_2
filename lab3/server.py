import socket
import json
import threading
import time

class GameServer:
    def __init__(self):
        self.players = []
        self.colors = ['white', 'black']
        self.running = True
        
    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', 5555))
        server.listen(2)
        
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    ШАШКИ - ОНЛАЙН СЕРВЕР                      ║
║                   Ожидание игроков (порт 5555)...              ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        # Подключаем двух игроков
        while len(self.players) < 2 and self.running:
            client, addr = server.accept()
            print(f"✅ Игрок подключился: {addr}")
            
            color = self.colors[len(self.players)]
            self.players.append(client)
            
            client.send((json.dumps({'type': 'color', 'color': color}) + '\n').encode())
            print(f"  -> Отправлен цвет: {color}")
        
        if not self.running:
            return
        
        print("\n🎮 ОБА ИГРОКА ПОДКЛЮЧЕНЫ! ИГРА НАЧИНАЕТСЯ!\n")
        
        # Отправляем сигнал старта
        for player in self.players:
            player.send((json.dumps({'type': 'start'}) + '\n').encode())
        print("✅ Сигнал старта отправлен\n")
        
        # Запускаем обработку ходов
        self.forward_moves()
    
    def forward_moves(self):
        """Пересылка ходов между игроками с буферизацией"""
        # Для каждого игрока свой буфер
        buffers = ['', '']
        
        while self.running:
            try:
                # Используем select для неблокирующего чтения
                import select
                readable, _, _ = select.select(self.players, [], [], 0.1)
                
                for sock in readable:
                    i = self.players.index(sock)
                    try:
                        data = sock.recv(4096).decode()
                        if data:
                            buffers[i] += data
                            # Разбираем все полные сообщения
                            while '\n' in buffers[i]:
                                line, buffers[i] = buffers[i].split('\n', 1)
                                if line.strip():
                                    msg = json.loads(line)
                                    if msg.get('type') == 'move':
                                        other = self.players[1 - i]
                                        move_data = json.dumps({'type': 'move', 'move': msg['move']}) + '\n'
                                        other.send(move_data.encode())
                                        print(f"🔄 Пересылка хода: {msg['move']} от игрока {i} -> {1-i}")
                    except Exception as e:
                        print(f"Ошибка при чтении от игрока {i}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Ошибка в forward_moves: {e}")
                pass
    
    def stop(self):
        self.running = False
        for player in self.players:
            try:
                player.close()
            except:
                pass

if __name__ == "__main__":
    server = GameServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
        server.stop()