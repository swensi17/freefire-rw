import os
import sys
import cv2
import json
import time
import numpy as np
import win32gui
import win32con
import win32ui
import win32api
import win32process
import keyboard
import threading
from win32com.client import GetObject
from PIL import Image
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, Property, QPoint, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QFont
from PySide6.QtWidgets import *
import logging
import psutil
import subprocess
import wmi

class BlinkingText(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._opacity = 1.0
        self.setStyleSheet("color: #00ff00; font-family: 'Courier New';")
        
        # Анимация мигания
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setLoopCount(-1)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.3)
        self.animation.setEasingCurve(QEasingCurve.InOutSine)
        self.animation.start()
        
    def getOpacity(self):
        return self._opacity
        
    def setOpacity(self, opacity):
        self._opacity = opacity
        self.setStyleSheet(f"color: #00ff00; font-family: 'Courier New';")
        
    opacity = Property(float, getOpacity, setOpacity)

class TerminalFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #333;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        # Заголовок терминала
        header = QFrame(self)
        header.setFixedHeight(30)
        header.setStyleSheet("""
            QFrame {
                background-color: #333;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin: 0;
            }
        """)
        
        # Кнопки управления
        controls = QHBoxLayout(header)
        controls.setContentsMargins(10, 0, 0, 0)
        controls.setSpacing(5)
        
        for color in ["#e33", "#ee0", "#0b0"]:
            btn = QLabel()
            btn.setFixedSize(12, 12)
            btn.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
            controls.addWidget(btn)
        
        controls.addStretch()
        
        # Layout для содержимого
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 40, 15, 15)
        self.layout.setSpacing(10)

class ToggleSwitch(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.setFixedSize(60, 34)
        self._checked = False
        self._value = 0.0  # Инициализируем значение
        self._main_window = main_window
        self._animation = QPropertyAnimation(self, b"value")
        self._animation.setDuration(400)
        
    def value(self):
        return self._value
        
    def setValue(self, value):
        self._value = value
        self.update()
        
    value = Property(float, value, setValue)
    
    def isChecked(self):
        return self._checked
        
    def mousePressEvent(self, event):
        if self._main_window:
            self._checked = not self._checked
            self._animation.setStartValue(0 if self._checked else 1)
            self._animation.setEndValue(1 if self._checked else 0)
            self._animation.start()
            self._main_window.toggle_aimbot()
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Рисуем фон
        track_color = QColor("#86d993") if self._checked else QColor("#e57373")
        p.setBrush(track_color)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, 60, 34, 17, 17)
        
        # Рисуем переключатель
        handle_color = QColor("#81da8f") if self._checked else QColor("#e66a6a")
        p.setBrush(handle_color)
        x = 30 * self._value + 4
        p.drawEllipse(int(x), 4, 26, 26)

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._offset = QPoint(0, 0)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #00ff00;
                border: 2px solid #00ff00;
                border-radius: 5px;
                padding: 15px;
                font-family: 'Courier New';
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #00ff00;
                color: #000000;
            }
        """)
        
        # Анимация при наведении
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(100)

    def enterEvent(self, event):
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(self.pos() + QPoint(0, -2))
        self.animation.start()

    def leaveEvent(self, event):
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(self.pos() + QPoint(0, 2))
        self.animation.start()

class FreeFire_Aimbot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.running = True
        self.game_window_handle = None
        self.frame_time = 0.1
        self.emulator_info = None
        self.in_game = False
        self.statistics = {
            'timestamp': '',
            'window_found': False,
            'window_title': '',
            'status': 'Инициализация',
            'emulator': 'Не обнаружен',
            'in_game': False
        }
        
        # Загружаем конфигурацию
        self.config = self.load_config()
        
        # Инициализируем без каскада
        self.classifier = None
        
        # Настройка логирования
        self.setup_logging()
        
        # Создание GUI
        self.create_gui()
        
        # Таймер для обновления статистики
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(1000)  # Обновление каждую секунду
        
        # Таймер для проверки эмулятора
        self.emulator_timer = QTimer()
        self.emulator_timer.timeout.connect(self.check_emulator)
        self.emulator_timer.start(5000)  # Проверка каждые 5 секунд
        
        self.logger.info("Скрипт успешно инициализирован")

    def setup_logging(self):
        self.logger.setLevel(logging.INFO)
        
        # Консольный вывод
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Файловый вывод
        file_handler = logging.FileHandler('aimbot.log')
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def detect_players(self, frame):
        try:
            start_time = time.time()
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
            
            players = self.classifier.detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=3,
                minSize=(20, 40),
                maxSize=(80, 160)
            )
            
            filtered_players = []
            for (x, y, w, h) in players:
                aspect_ratio = h/w
                if 1.5 <= aspect_ratio <= 3.0:
                    filtered_players.append((x, y, w, h))
            
            # Обновляем FPS
            end_time = time.time()
            fps = 1.0 / (end_time - start_time)
            
            # Обновляем информацию о последнем обнаружении
            last_detection = {
                'players_found': len(filtered_players),
                'timestamp': time.strftime('%H:%M:%S')
            }
            
            return [(box, 1.0) for box in filtered_players]
            
        except Exception as e:
            self.logger.error(f"Ошибка обнаружения игроков: {e}")
            return []

    def update_stats(self):
        try:
            self.statistics.update({
                'timestamp': time.strftime('%H:%M:%S'),
                'window_found': self.game_window_handle is not None,
                'window_title': win32gui.GetWindowText(self.game_window_handle) if self.game_window_handle else 'Не найдено',
                'status': 'Активен' if self.running else 'Остановлен',
                'emulator': self.emulator_info['name'] if self.emulator_info else 'Не обнаружен',
                'in_game': self.in_game
            })
        except Exception as e:
            self.logger.error(f"Ошибка обновления статистики: {e}")

    def check_emulator(self):
        try:
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    if proc.name() in ['HD-Player.exe', 'MEmu.exe', 'NoxPlayer.exe']:
                        self.emulator_info = {
                            'name': proc.name().replace('.exe', ''),
                            'pid': proc.pid,
                            'path': proc.exe() if proc.exe() else 'Путь не доступен'
                        }
                        return
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.emulator_info = None
            self.logger.warning("Эмулятор не обнаружен. Проверьте, что HD-Player запущен.")
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке эмулятора: {e}")
            self.emulator_info = None

    def create_gui(self):
        self.setWindowTitle("NAS Panel | Free Fire MAX")
        self.setFixedSize(500, 700)
        
        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        
        # Терминал статуса
        status_terminal = TerminalFrame()
        main_layout.addWidget(status_terminal)
        
        # Статус и переключатель
        status_layout = QHBoxLayout()
        self.status_label = BlinkingText("STATUS: OFF")
        status_layout.addWidget(self.status_label)
        
        self.toggle_switch = ToggleSwitch(main_window=self)  # Передаем ссылку на главное окно
        status_layout.addWidget(self.toggle_switch)
        status_terminal.layout.addLayout(status_layout)
        
        # Терминал статистики
        stats_terminal = TerminalFrame()
        main_layout.addWidget(stats_terminal)
        
        # Статистика
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 12px;
                background-color: transparent;
            }
        """)
        stats_terminal.layout.addWidget(self.stats_label)
        
        # Общий стиль окна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
            }
        """)

    def toggle_aimbot(self):
        self.aimbot_enabled = not self.aimbot_enabled
        if self.aimbot_enabled:
            if not self.running:
                self.running = True
                self.aimbot_thread = threading.Thread(target=self.aimbot_loop)
                self.aimbot_thread.daemon = True
                self.aimbot_thread.start()
                self.logger.info("Аимбот активирован")
            self.status_label.setText("STATUS: ACTIVE")
            self.status_label.setStyleSheet("color: #00ff00; font-family: 'Courier New';")
        else:
            self.status_label.setText("STATUS: INACTIVE")
            self.status_label.setStyleSheet("color: #ff0000; font-family: 'Courier New';")
            self.logger.info("Аимбот деактивирован")

    def launch_free_fire(self):
        try:
            # Путь к MSI App Player
            emulator_path = "C:/Program Files (x86)/MSI App Player/AppPlayer.exe"
            
            if os.path.exists(emulator_path):
                print("[+] Запуск Free Fire в MSI App Player...")
                # Запускаем эмулятор
                subprocess.Popen([emulator_path])
                time.sleep(15)  # Ждем загрузки эмулятора
                
                # Запускаем Free Fire
                subprocess.Popen([emulator_path, "--apk", "com.dts.freefireth"])
                time.sleep(10)  # Ждем загрузки игры
            else:
                print("[-] MSI App Player не найден")
        except Exception as e:
            print(f"[-] Ошибка запуска Free Fire: {e}")

    def load_config(self):
        config_path = "config.json"
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        return {
            "sensitivity": 1.0,
            "head_offset": 25,
            "exit_key": "end",
            "window_name": "MSI App Player"
        }
        
    def save_config(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=4)
            
    def load_models(self):
        try:
            # Используем каскадный классификатор вместо YOLO для более быстрой работы
            cascade_path = "haarcascade_upperbody.xml"
            if not os.path.exists(cascade_path):
                print("[!] Загрузка классификатора...")
                import urllib.request
                url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_upperbody.xml"
                urllib.request.urlretrieve(url, cascade_path)
            
            self.classifier = cv2.CascadeClassifier(cascade_path)
            print("[+] Классификатор успешно загружен")
        except Exception as e:
            print(f"[-] Ошибка загрузки классификатора: {e}")
            
    def find_game_window(self):
        try:
            # Список возможных названий окна и классов
            window_patterns = [
                "MSI App Player",
                "HD-Player",
                "Free Fire",
                "NAS Panel"
            ]
            
            window_classes = [
                "Qt5154QWindowOwnDCIcon",
                "Qt5QWindowIcon",
                "Qt5QWindow"
            ]
            
            found_windows = []
            
            def callback(hwnd, ctx):
                if not win32gui.IsWindowVisible(hwnd):
                    return True
                
                try:
                    title = win32gui.GetWindowText(hwnd)
                    class_name = win32gui.GetClassName(hwnd)
                    
                    if not title:
                        return True
                    
                    # Проверяем название окна и класс
                    title_match = any(pattern.lower() in title.lower() for pattern in window_patterns)
                    class_match = any(wc in class_name for wc in window_classes)
                    
                    if title_match or class_match:
                        # Проверяем размер окна
                        rect = win32gui.GetWindowRect(hwnd)
                        width = rect[2] - rect[0]
                        height = rect[3] - rect[1]
                        
                        if width > 100 and height > 100:
                            found_windows.append({
                                'hwnd': hwnd,
                                'title': title,
                                'class': class_name,
                                'size': (width, height)
                            })
                except Exception as e:
                    self.logger.error(f"Ошибка при проверке окна: {e}")
                return True

            win32gui.EnumWindows(callback, None)
            
            # Приоритет окон
            for pattern in ["Free Fire", "MSI App Player", "HD-Player", "NAS Panel"]:
                for window in found_windows:
                    if pattern.lower() in window['title'].lower():
                        self.logger.info(f"Выбрано окно: {window['title']} ({window['size'][0]}x{window['size'][1]})")
                        self.game_window_handle = window['hwnd']
                        return window['hwnd']
            
            if found_windows:
                window = found_windows[0]
                self.logger.info(f"Выбрано первое доступное окно: {window['title']}")
                self.game_window_handle = window['hwnd']
                return window['hwnd']
                
            return None

        except Exception as e:
            self.logger.error(f"Ошибка при поиске окна: {e}")
            return None

    def process_game_screen(self, screen):
        try:
            if screen is None:
                return None

            # Определяем размеры экрана
            height, width = screen.shape[:2]

            # Создаем маску для определения цвета кожи в HSV
            hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
            
            # Расширенные диапазоны для определения кожи
            skin_ranges = [
                # Основные диапазоны для кожи
                (np.array([0, 20, 70]), np.array([20, 150, 255])),      # Базовый тон
                (np.array([0, 30, 60]), np.array([25, 180, 255])),      # Светлая кожа
                (np.array([0, 10, 50]), np.array([30, 160, 255])),      # Темная кожа
                # Дополнительные диапазоны для лучшего обнаружения
                (np.array([5, 25, 65]), np.array([25, 165, 255])),      # Средний тон 1
                (np.array([10, 15, 55]), np.array([35, 170, 255])),     # Средний тон 2
            ]
            
            # Создаем общую маску кожи
            skin_mask = np.zeros((height, width), dtype=np.uint8)
            for lower, upper in skin_ranges:
                current_mask = cv2.inRange(hsv, lower, upper)
                skin_mask = cv2.bitwise_or(skin_mask, current_mask)

            # Улучшаем маску морфологическими операциями
            kernel_open = np.ones((3,3), np.uint8)
            kernel_close = np.ones((7,7), np.uint8)
            
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel_open)
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel_close)
            skin_mask = cv2.dilate(skin_mask, kernel_close, iterations=1)

            # Определяем несколько областей для поиска головы
            head_regions = [
                # Центральная область (основная)
                {
                    'y1': int(height * 0.05),
                    'y2': int(height * 0.45),
                    'x1': int(width * 0.35),
                    'x2': int(width * 0.65),
                    'threshold': 300
                },
                # Верхняя область (для высоких персонажей)
                {
                    'y1': int(height * 0.0),
                    'y2': int(height * 0.35),
                    'x1': int(width * 0.4),
                    'x2': int(width * 0.6),
                    'threshold': 200
                },
                # Нижняя область (для присевших персонажей)
                {
                    'y1': int(height * 0.15),
                    'y2': int(height * 0.5),
                    'x1': int(width * 0.3),
                    'x2': int(width * 0.7),
                    'threshold': 400
                }
            ]

            head_found = False
            for region in head_regions:
                # Проверяем наличие кожи в текущей области
                head_region = skin_mask[region['y1']:region['y2'], 
                                     region['x1']:region['x2']]
                
                if cv2.countNonZero(head_region) > region['threshold']:
                    # Создаем градиентную маску для плавного перехода
                    gradient_mask = np.zeros((region['y2'] - region['y1'], 
                                           region['x2'] - region['x1'], 3), 
                                           dtype=np.uint8)
                    
                    # Закрашиваем область головы черным с градиентом
                    screen[region['y1']:region['y2'], 
                          region['x1']:region['x2']] = gradient_mask
                    
                    head_found = True
                    self.logger.info(f"Голова найдена и скрыта в области {region}")
                    break

            self.in_game = head_found
            return screen

        except Exception as e:
            self.logger.error(f"Ошибка при обработке экрана: {e}")
            return screen

    def capture_screen(self):
        try:
            # Ищем окно игры
            hwnd = self.find_game_window()
            if not hwnd:
                self.logger.warning("Эмулятор не обнаружен. Проверьте, что HD-Player запущен.")
                return None

            # Сохраняем handle окна
            self.game_window_handle = hwnd

            # Проверяем, что окно не свернуто
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.1)  # Даем время на восстановление окна

            return self.get_screen(hwnd)

        except Exception as e:
            self.logger.error(f"Ошибка захвата экрана: {str(e)}")
            return None

    def get_screen(self, hwnd):
        try:
            if not hwnd or not win32gui.IsWindow(hwnd):
                self.logger.error("Недопустимый дескриптор окна")
                return None

            # Получаем размеры окна
            try:
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width = right - left
                height = bottom - top
            except Exception as e:
                self.logger.error(f"Ошибка получения размеров окна: {e}")
                return None

            if width <= 0 or height <= 0:
                self.logger.error(f"Некорректные размеры окна: {width}x{height}")
                return None

            try:
                # Используем PIL для создания скриншота
                import PIL.ImageGrab
                screenshot = PIL.ImageGrab.grab(bbox=(left, top, right, bottom))
                
                # Конвертируем в numpy array
                screen_np = np.array(screenshot)
                
                # Конвертируем из RGB в BGR для OpenCV
                screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
                
                return screen_bgr

            except Exception as e:
                self.logger.error(f"Ошибка при создании скриншота: {e}")
                return None

        except Exception as e:
            self.logger.error(f"Ошибка получения скриншота: {str(e)}")
            return None

    def aim_at_target(self, target_x, target_y, width, height):
        try:
            center_x = width // 2
            center_y = height // 2
            
            # Улучшенный алгоритм прицеливания
            dx = (target_x - center_x) * self.sensitivity
            dy = (target_y - center_y - self.head_offset) * self.sensitivity
            
            # Плавное движение с предсказанием
            steps = 5  # Уменьшено для более быстрого прицеливания
            for i in range(steps):
                move_x = int(dx/steps)
                move_y = int(dy/steps)
                
                # Добавляем небольшую коррекцию для компенсации движения
                if i == steps - 1:
                    move_x += int(dx * 0.1)
                    move_y += int(dy * 0.1)
                
                win32api.mouse_event(
                    win32con.MOUSEEVENTF_MOVE,
                    move_x,
                    move_y,
                    0, 0
                )
                time.sleep(0.001)
                
        except Exception as e:
            print(f"[-] Ошибка прицеливания: {e}")

    def update_sensitivity(self, value):
        self.sensitivity = value / 50.0
        self.config["sensitivity"] = self.sensitivity
        self.save_config()

    def update_head_offset(self, value):
        self.head_offset = value
        self.config["head_offset"] = self.head_offset
        self.save_config()

    def closeEvent(self, event):
        self.running = False
        self.save_config()
        event.accept()

    def check_game_state(self):
        try:
            screen = self.capture_screen()
            if screen is None:
                return
            
            # Конвертируем в HSV для лучшего определения цветов
            hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
            
            # Определяем размеры экрана
            height, width = screen.shape[:2]
            
            # Проверяем наличие элементов интерфейса
            ui_detected = self.check_ui_elements(hsv)
            
            if ui_detected:
                self.logger.info("Обнаружен игровой интерфейс")
                
                # Определяем область головы персонажа в лобби
                lobby_head_region = {
                    'x1': int(width * 0.45),  # Примерное положение головы
                    'y1': int(height * 0.2),
                    'x2': int(width * 0.55),
                    'y2': int(height * 0.35)
                }
                
                # Проверяем, находимся ли мы в лобби
                lobby_colors = self.check_lobby_colors(hsv)
                if lobby_colors:
                    self.logger.info("Персонаж находится в лобби")
                    # Скрываем голову персонажа
                    cv2.rectangle(screen, 
                                (lobby_head_region['x1'], lobby_head_region['y1']),
                                (lobby_head_region['x2'], lobby_head_region['y2']),
                                (0, 0, 0), -1)  # Черный прямоугольник
                
                # Проверяем видимость персонажа
                character_visible = self.check_character_visibility(hsv)
                if character_visible:
                    self.logger.info("Персонаж обнаружен в правильном положении")
            
            self.game_state = {
                'ui_detected': ui_detected,
                'in_lobby': lobby_colors if 'lobby_colors' in locals() else False,
                'character_visible': character_visible if 'character_visible' in locals() else False
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке состояния игры: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def check_lobby_colors(self, hsv):
        try:
            # Определяем характерные цвета лобби
            lobby_lower = np.array([0, 0, 100])  # Светлые тона
            lobby_upper = np.array([180, 30, 255])
            
            # Создаем маску для цветов лобби
            lobby_mask = cv2.inRange(hsv, lobby_lower, lobby_upper)
            
            # Проверяем количество пикселей характерного цвета
            lobby_pixels = cv2.countNonZero(lobby_mask)
            
            # Если больше 10% пикселей соответствуют цветам лобби
            return lobby_pixels > (hsv.shape[0] * hsv.shape[1] * 0.1)
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке цветов лобби: {e}")
            return False

    def check_ui_elements(self, hsv):
        try:
            # Определяем цветовые диапазоны для UI элементов (расширенный диапазон)
            ui_masks = []
            # Белый цвет (интерфейс)
            ui_masks.append(cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 30, 255])))
            # Зеленый цвет (здоровье)
            ui_masks.append(cv2.inRange(hsv, np.array([40, 100, 100]), np.array([80, 255, 255])))
            # Красный цвет (кровь, урон)
            ui_masks.append(cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255])))
            
            # Объединяем маски
            ui_mask = sum(ui_masks)
            ui_elements = cv2.countNonZero(ui_mask)
            
            # Если найдено достаточно UI элементов
            return ui_elements > 1000
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке UI элементов: {e}")
            return False

    def check_character_visibility(self, hsv):
        try:
            # Определяем телесные тона (расширенный диапазон)
            skin_masks = []
            # Светлая кожа
            skin_masks.append(cv2.inRange(hsv, np.array([0, 20, 70]), np.array([20, 150, 255])))
            # Темная кожа
            skin_masks.append(cv2.inRange(hsv, np.array([0, 10, 50]), np.array([30, 180, 200])))
            
            # Объединяем маски
            skin_mask = sum(skin_masks)
            
            # Проверяем количество пикселей телесного цвета
            skin_pixels = cv2.countNonZero(skin_mask)
            
            # Если найдено достаточно пикселей телесного цвета
            return skin_pixels > 500
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке видимости персонажа: {e}")
            return False

    def update_statistics(self):
        try:
            self.statistics = {
                'timestamp': time.strftime('%H:%M:%S'),
                'window_found': self.game_window_handle is not None,
                'window_title': win32gui.GetWindowText(self.game_window_handle) if self.game_window_handle else '',
                'status': 'Активен' if self.running else 'Остановлен'
            }
        except Exception as e:
            self.logger.error(f"Ошибка обновления статистики: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    aimbot = FreeFire_Aimbot()
    aimbot.show()
    sys.exit(app.exec())
