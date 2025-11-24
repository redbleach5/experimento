"""
Современный GUI интерфейс для AI Code Agent
Использует tkinter с современным дизайном
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import subprocess
import os
import sys
from pathlib import Path
import json
from datetime import datetime
from agent import CodeAgent
import requests
import yaml

# Цветовая схема
COLORS = {
    'bg_main': '#1e1e1e',
    'bg_secondary': '#252526',
    'bg_tertiary': '#2d2d30',
    'fg_main': '#cccccc',
    'fg_secondary': '#858585',
    'accent': '#007acc',
    'accent_hover': '#0098ff',
    'success': '#4ec9b0',
    'warning': '#dcdcaa',
    'error': '#f48771',
    'code_bg': '#1e1e1e',
    'code_fg': '#d4d4d4',
}


class ModernScrollbar(ttk.Scrollbar):
    """Кастомный скроллбар"""
    def __init__(self, *args, **kwargs):
        kwargs['style'] = 'Modern.TScrollbar'
        super().__init__(*args, **kwargs)


class CodeAgentGUI:
    """Главное окно приложения"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AI Code Agent 🤖")
        self.root.geometry("1200x800")
        self.root.configure(bg=COLORS['bg_main'])
        
        # Инициализация агента
        self.agent = None
        self.agent_ready = False
        self.current_model = None
        
        # Очередь для обновления UI из других потоков
        self.message_queue = queue.Queue()
        
        # Настройка стилей
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Проверка Ollama при запуске
        self.check_ollama_async()
        
        # Обработка очереди сообщений
        self.root.after(100, self.process_queue)
    
    def setup_styles(self):
        """Настройка стилей ttk"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка цветов для ttk виджетов
        style.configure('TFrame', background=COLORS['bg_main'])
        style.configure('TLabel', background=COLORS['bg_main'], foreground=COLORS['fg_main'])
        style.configure('TButton', background=COLORS['accent'], foreground='white')
        style.map('TButton',
                  background=[('active', COLORS['accent_hover']),
                             ('pressed', COLORS['accent'])])
        style.configure('TEntry', fieldbackground=COLORS['bg_tertiary'],
                       foreground=COLORS['fg_main'], borderwidth=1)
        style.configure('TCombobox', fieldbackground=COLORS['bg_tertiary'],
                      foreground=COLORS['fg_main'])
        style.configure('Modern.TScrollbar', background=COLORS['bg_secondary'],
                       troughcolor=COLORS['bg_main'], borderwidth=0,
                       arrowcolor=COLORS['fg_secondary'])
    
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Верхняя панель
        self.create_header()
        
        # Основная область
        main_container = tk.Frame(self.root, bg=COLORS['bg_main'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель (настройки и статус)
        self.create_sidebar(main_container)
        
        # Центральная область (чат)
        self.create_chat_area(main_container)
        
        # Нижняя панель (ввод)
        self.create_input_area()
    
    def create_header(self):
        """Создание верхней панели"""
        header = tk.Frame(self.root, bg=COLORS['bg_secondary'], height=60)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        # Заголовок
        title_label = tk.Label(
            header,
            text="🤖 AI Code Agent",
            font=('Segoe UI', 18, 'bold'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_main']
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Статус
        self.status_label = tk.Label(
            header,
            text="⏳ Проверка Ollama...",
            font=('Segoe UI', 10),
            bg=COLORS['bg_secondary'],
            fg=COLORS['warning']
        )
        self.status_label.pack(side=tk.RIGHT, padx=20, pady=15)
    
    def create_sidebar(self, parent):
        """Создание боковой панели"""
        sidebar = tk.Frame(parent, bg=COLORS['bg_secondary'], width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Заголовок настроек
        settings_title = tk.Label(
            sidebar,
            text="⚙️ Настройки",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_main']
        )
        settings_title.pack(pady=(15, 10), padx=15, anchor=tk.W)
        
        # Выбор провайдера
        provider_frame = tk.Frame(sidebar, bg=COLORS['bg_secondary'])
        provider_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            provider_frame,
            text="Провайдер:",
            font=('Segoe UI', 9),
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_secondary']
        ).pack(anchor=tk.W)
        
        self.provider_var = tk.StringVar(value="ollama")
        provider_combo = ttk.Combobox(
            provider_frame,
            textvariable=self.provider_var,
            values=["ollama", "lmstudio"],
            state='readonly',
            width=20
        )
        provider_combo.pack(fill=tk.X, pady=(5, 0))
        provider_combo.bind('<<ComboboxSelected>>', self.on_provider_change)
        
        # Выбор модели
        model_frame = tk.Frame(sidebar, bg=COLORS['bg_secondary'])
        model_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            model_frame,
            text="Модель:",
            font=('Segoe UI', 9),
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_secondary']
        ).pack(anchor=tk.W)
        
        # Загружаем модель из конфига по умолчанию
        default_model = "qwen3-30b-a3b-instruct-2507"
        try:
            import yaml
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                default_model = config.get('model', {}).get('model_name', default_model)
        except:
            pass
        
        self.model_var = tk.StringVar(value=default_model)
        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=[default_model],  # Начальный список, будет обновлен
            state='readonly',
            width=25
        )
        self.model_combo.pack(fill=tk.X, pady=(5, 0))
        self.model_combo.bind('<<ComboboxSelected>>', self.on_model_change)
        
        # Кнопка обновления моделей
        refresh_btn = tk.Button(
            sidebar,
            text="🔄 Обновить список моделей",
            font=('Segoe UI', 9),
            bg=COLORS['bg_tertiary'],
            fg=COLORS['fg_main'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self.refresh_models
        )
        refresh_btn.pack(fill=tk.X, padx=15, pady=5)
        
        # Кнопка установки модели
        install_btn = tk.Button(
            sidebar,
            text="📥 Установить модель",
            font=('Segoe UI', 9),
            bg=COLORS['accent'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.install_model
        )
        install_btn.pack(fill=tk.X, padx=15, pady=5)
        
        # Разделитель
        separator = tk.Frame(sidebar, bg=COLORS['bg_tertiary'], height=1)
        separator.pack(fill=tk.X, padx=15, pady=15)
        
        # Информация о системе
        info_title = tk.Label(
            sidebar,
            text="ℹ️ Информация",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_main']
        )
        info_title.pack(pady=(0, 10), padx=15, anchor=tk.W)
        
        self.info_text = tk.Text(
            sidebar,
            bg=COLORS['bg_tertiary'],
            fg=COLORS['fg_secondary'],
            font=('Consolas', 9),
            wrap=tk.WORD,
            height=8,
            relief=tk.FLAT,
            borderwidth=0,
            padx=10,
            pady=10
        )
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        self.info_text.insert('1.0', "Ожидание инициализации...")
        self.info_text.config(state=tk.DISABLED)
        
        # Кнопки действий
        actions_frame = tk.Frame(sidebar, bg=COLORS['bg_secondary'])
        actions_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        clear_btn = tk.Button(
            actions_frame,
            text="🗑️ Очистить чат",
            font=('Segoe UI', 9),
            bg=COLORS['bg_tertiary'],
            fg=COLORS['fg_main'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self.clear_chat
        )
        clear_btn.pack(fill=tk.X, pady=2)
        
        save_btn = tk.Button(
            actions_frame,
            text="💾 Сохранить историю",
            font=('Segoe UI', 9),
            bg=COLORS['bg_tertiary'],
            fg=COLORS['fg_main'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self.save_history
        )
        save_btn.pack(fill=tk.X, pady=2)
    
    def create_chat_area(self, parent):
        """Создание области чата"""
        chat_frame = tk.Frame(parent, bg=COLORS['bg_main'])
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Текстовая область чата
        self.chat_text = scrolledtext.ScrolledText(
            chat_frame,
            bg=COLORS['code_bg'],
            fg=COLORS['code_fg'],
            font=('Consolas', 11),
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=0,
            padx=20,
            pady=20,
            insertbackground=COLORS['fg_main']
        )
        self.chat_text.pack(fill=tk.BOTH, expand=True)
        
        # Приветственное сообщение
        welcome_msg = """╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🤖 AI Code Agent - Локальный помощник          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Привет! Я AI-ассистент для программирования. Задайте мне вопрос о коде, и я помогу вам!

Примеры запросов:
  • "Напиши функцию для сортировки массива на Python"
  • "Объясни разницу между async и await в JavaScript"
  • "Создай REST API на FastAPI с аутентификацией"

"""
        self.add_message(welcome_msg, 'system')
    
    def create_input_area(self):
        """Создание области ввода"""
        input_frame = tk.Frame(self.root, bg=COLORS['bg_secondary'], height=120)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        input_frame.pack_propagate(False)
        
        # Текстовое поле ввода
        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            bg=COLORS['bg_tertiary'],
            fg=COLORS['fg_main'],
            font=('Segoe UI', 10),
            wrap=tk.WORD,
            height=4,
            relief=tk.FLAT,
            borderwidth=1,
            padx=15,
            pady=15,
            insertbackground=COLORS['fg_main']
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.input_text.bind('<Control-Return>', lambda e: self.send_message())
        self.input_text.bind('<KeyPress>', self.on_input_key)
        
        # Кнопка отправки
        button_frame = tk.Frame(input_frame, bg=COLORS['bg_secondary'])
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.send_button = tk.Button(
            button_frame,
            text="📤 Отправить (Ctrl+Enter)",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORS['accent'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=8,
            command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Индикатор генерации
        self.generating_label = tk.Label(
            button_frame,
            text="",
            font=('Segoe UI', 9),
            bg=COLORS['bg_secondary'],
            fg=COLORS['warning']
        )
        self.generating_label.pack(side=tk.LEFT, padx=10)
    
    def on_input_key(self, event):
        """Обработка нажатий клавиш в поле ввода"""
        if event.state == 4 and event.keysym == 'Return':  # Ctrl+Enter
            self.send_message()
            return 'break'
    
    def check_ollama_async(self):
        """Асинхронная проверка Ollama и LM Studio"""
        def check():
            provider = self.provider_var.get()
            
            if provider == "ollama":
                try:
                    result = subprocess.run(
                        ['ollama', '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        self.message_queue.put(('status', 'success', 'Ollama установлен'))
                        self.load_models()
                    else:
                        self.message_queue.put(('status', 'error', 'Ollama не найден'))
                except FileNotFoundError:
                    self.message_queue.put(('status', 'error', 'Ollama не установлен. Установите с https://ollama.ai'))
                except Exception as e:
                    self.message_queue.put(('status', 'error', f'Ошибка: {str(e)}'))
            
            elif provider == "lmstudio":
                try:
                    response = requests.get('http://localhost:1234/v1/models', timeout=5)
                    if response.status_code == 200:
                        self.message_queue.put(('status', 'success', 'LM Studio подключен'))
                        self.load_models()
                    else:
                        self.message_queue.put(('status', 'error', 'LM Studio недоступен. Включите Local Server'))
                except Exception as e:
                    self.message_queue.put(('status', 'error', f'LM Studio не доступен: {str(e)}'))
                    self.message_queue.put(('status', 'warning', 'Убедитесь, что LM Studio запущен и Local Server включен'))
        
        threading.Thread(target=check, daemon=True).start()
    
    def load_models(self):
        """Загрузка списка моделей"""
        def load():
            provider = self.provider_var.get()
            
            try:
                if provider == "ollama":
                    response = requests.get('http://localhost:11434/api/tags', timeout=5)
                    if response.status_code == 200:
                        models = response.json().get('models', [])
                        model_names = [m['name'] for m in models]
                        self.message_queue.put(('models', model_names))
                        
                        # Инициализация агента
                        if model_names:
                            self.message_queue.put(('status', 'success', f'Готов к работе ({len(model_names)} моделей)'))
                            self.init_agent()
                        else:
                            self.message_queue.put(('status', 'warning', 'Модели не установлены'))
                    else:
                        self.message_queue.put(('status', 'error', 'Ollama недоступен'))
                
                elif provider == "lmstudio":
                    # Пробуем несколько раз с разными таймаутами
                    model_names = []
                    base_url = 'http://127.0.0.1:1234'
                    
                    for attempt in range(3):
                        try:
                            timeout = 5 + (attempt * 5)  # 5, 10, 15 секунд
                            response = requests.get(f'{base_url}/v1/models', timeout=timeout)
                            
                            if response.status_code == 200:
                                data = response.json()
                                models = data.get('data', [])
                                
                                # Извлекаем все возможные идентификаторы
                                for m in models:
                                    model_id = m.get('id') or m.get('model') or m.get('name') or ''
                                    if model_id and model_id not in model_names:
                                        model_names.append(model_id)
                                
                                if model_names:
                                    break
                            elif response.status_code == 502 and attempt < 2:
                                # Если 502, ждем и пробуем снова
                                import time
                                time.sleep((attempt + 1) * 3)
                                continue
                                
                        except requests.exceptions.Timeout:
                            if attempt < 2:
                                continue
                        except requests.exceptions.ConnectionError:
                            if attempt < 2:
                                import time
                                time.sleep(2)
                                continue
                        except Exception as e:
                            if attempt < 2:
                                import time
                                time.sleep(2)
                                continue
                    
                    # Отправляем список моделей в GUI
                    if model_names:
                        self.message_queue.put(('models', model_names))
                        self.message_queue.put(('status', 'success', f'Найдено моделей: {len(model_names)}'))
                        # Показываем список моделей
                        models_list = ', '.join(model_names[:5])
                        if len(model_names) > 5:
                            models_list += f' и еще {len(model_names) - 5}'
                        self.message_queue.put(('status', 'info', f'Модели: {models_list}'))
                        self.init_agent()
                    else:
                        # Если модели не найдены через API, используем модель из конфига
                        try:
                            import yaml
                            with open('config.yaml', 'r', encoding='utf-8') as f:
                                config = yaml.safe_load(f)
                            config_model = config.get('model', {}).get('model_name', '')
                            
                            if config_model:
                                # Добавляем модель из конфига в список
                                model_names = [config_model]
                                self.message_queue.put(('models', model_names))
                                self.message_queue.put(('status', 'warning', f'API не отвечает. Используется модель из конфига: {config_model}'))
                                self.message_queue.put(('status', 'info', 'Если модель не работает, проверьте настройки LM Studio'))
                                self.init_agent()
                            else:
                                # Пробуем стандартные имена моделей
                                default_models = [
                                    'qwen3-30b-a3b-instruct-2507',
                                    'qwen3-30b-a3b-instruct',
                                    'qwen3-30b',
                                    'qwen3'
                                ]
                                self.message_queue.put(('models', default_models))
                                self.message_queue.put(('status', 'warning', 'API не отвечает. Выберите модель вручную'))
                                self.message_queue.put(('status', 'info', 'Проверьте, что модель загружена в LM Studio'))
                        except Exception as e:
                            # В крайнем случае показываем стандартные модели
                            default_models = ['qwen3-30b-a3b-instruct-2507']
                            self.message_queue.put(('models', default_models))
                            self.message_queue.put(('status', 'error', f'Ошибка загрузки: {str(e)}'))
                            self.message_queue.put(('status', 'info', 'Используйте модель из списка'))
                        
            except Exception as e:
                self.message_queue.put(('status', 'error', f'Ошибка подключения: {str(e)}'))
        
        threading.Thread(target=load, daemon=True).start()
    
    def init_agent(self):
        """Инициализация агента"""
        try:
            # Обновляем конфигурацию с выбранным провайдером
            config_path = "config.yaml"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                config['model']['provider'] = self.provider_var.get()
                if self.model_var.get():
                    config['model']['model_name'] = self.model_var.get()
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            
            self.agent = CodeAgent()
            self.agent_ready = True
            self.current_model = self.agent.model_name
            self.message_queue.put(('agent_ready', True))
        except Exception as e:
            self.message_queue.put(('status', 'error', f'Ошибка инициализации: {str(e)}'))
    
    def on_provider_change(self, event=None):
        """Обработка изменения провайдера"""
        provider = self.provider_var.get()
        self.status_label.config(text=f"🔄 Переключение на {provider}...", fg=COLORS['warning'])
        self.agent_ready = False
        self.send_button.config(state=tk.DISABLED)
        self.check_ollama_async()
    
    def refresh_models(self):
        """Обновление списка моделей"""
        self.status_label.config(text="🔄 Обновление списка моделей...", fg=COLORS['warning'])
        self.load_models()
    
    def install_model(self):
        """Установка модели через Ollama"""
        model_name = self.model_var.get()
        if not model_name:
            messagebox.showwarning("Предупреждение", "Выберите модель для установки")
            return
        
        result = messagebox.askyesno(
            "Установка модели",
            f"Установить модель {model_name}?\n\nЭто может занять несколько минут и потребует ~4-7 GB места."
        )
        
        if result:
            self.status_label.config(text=f"📥 Установка {model_name}...", fg=COLORS['warning'])
            self.send_button.config(state=tk.DISABLED)
            
            def install():
                try:
                    process = subprocess.Popen(
                        ['ollama', 'pull', model_name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    output, error = process.communicate()
                    
                    if process.returncode == 0:
                        self.message_queue.put(('status', 'success', f'Модель {model_name} установлена'))
                        self.load_models()
                    else:
                        self.message_queue.put(('status', 'error', f'Ошибка установки: {error}'))
                except Exception as e:
                    self.message_queue.put(('status', 'error', f'Ошибка: {str(e)}'))
                finally:
                    self.message_queue.put(('install_done',))
            
            threading.Thread(target=install, daemon=True).start()
    
    def on_model_change(self, event=None):
        """Обработка изменения модели"""
        if self.agent_ready:
            new_model = self.model_var.get()
            # Обновление конфигурации потребует перезапуска агента
            messagebox.showinfo(
                "Изменение модели",
                f"Модель изменена на {new_model}.\nПерезапустите приложение для применения изменений."
            )
    
    def process_queue(self):
        """Обработка очереди сообщений"""
        try:
            while True:
                msg = self.message_queue.get_nowait()
                msg_type = msg[0]
                
                if msg_type == 'status':
                    status_type, text = msg[1], msg[2]
                    color = COLORS.get(status_type, COLORS['fg_main'])
                    self.status_label.config(text=text, fg=color)
                
                elif msg_type == 'models':
                    models = msg[1]
                    current = self.model_var.get()
                    self.model_combo['values'] = models
                    if current not in models and models:
                        self.model_var.set(models[0])
                
                elif msg_type == 'agent_ready':
                    self.send_button.config(state=tk.NORMAL)
                    self.update_info()
                
                elif msg_type == 'install_done':
                    self.send_button.config(state=tk.NORMAL)
                
                elif msg_type == 'chunk':
                    chunk = msg[1]
                    self.append_to_response(chunk)
                
                elif msg_type == 'response_done':
                    self.generating_label.config(text="")
                    self.send_button.config(state=tk.NORMAL)
                    self.input_text.config(state=tk.NORMAL)
        
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_queue)
    
    def update_info(self):
        """Обновление информации о системе"""
        if self.agent:
            provider_name = "Ollama" if self.agent.provider == "ollama" else "LM Studio"
            info = f"""Провайдер: {provider_name}
Модель: {self.agent.model_name}
Статус: Готов к работе

Для RTX 3090 рекомендуется:
• deepseek-coder:6.7b
• codellama:13b
• qwen2.5-coder:7b

LM Studio:
• Включите Local Server
• Загрузите модель в LM Studio
• Порт по умолчанию: 1234"""
        else:
            info = "Ожидание инициализации..."
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete('1.0', tk.END)
        self.info_text.insert('1.0', info)
        self.info_text.config(state=tk.DISABLED)
    
    def add_message(self, text, role='user'):
        """Добавление сообщения в чат"""
        self.chat_text.config(state=tk.NORMAL)
        
        if role == 'user':
            prefix = "👤 Вы:\n"
            tag = 'user'
        elif role == 'assistant':
            prefix = "🤖 AI Agent:\n"
            tag = 'assistant'
        else:
            prefix = ""
            tag = 'system'
        
        self.chat_text.insert(tk.END, prefix, tag)
        self.chat_text.insert(tk.END, text + "\n\n")
        
        # Настройка тегов для форматирования
        self.chat_text.tag_config('user', foreground=COLORS['accent'])
        self.chat_text.tag_config('assistant', foreground=COLORS['success'])
        self.chat_text.tag_config('system', foreground=COLORS['fg_secondary'])
        
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)
    
    def append_to_response(self, chunk):
        """Добавление части ответа"""
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, chunk)
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def send_message(self):
        """Отправка сообщения"""
        if not self.agent_ready:
            messagebox.showwarning("Не готов", "Агент еще не инициализирован. Подождите...")
            return
        
        user_input = self.input_text.get('1.0', tk.END).strip()
        if not user_input:
            return
        
        # Добавляем сообщение пользователя
        self.add_message(user_input, 'user')
        
        # Очищаем поле ввода
        self.input_text.delete('1.0', tk.END)
        self.input_text.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        self.generating_label.config(text="⏳ Генерируется ответ...")
        
        # Добавляем заголовок ответа
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, "🤖 AI Agent:\n", 'assistant')
        self.chat_text.config(state=tk.DISABLED)
        
        # Генерируем ответ в отдельном потоке
        def generate():
            try:
                for chunk in self.agent.ask(user_input, stream=True):
                    self.message_queue.put(('chunk', chunk))
                self.message_queue.put(('response_done',))
            except Exception as e:
                self.message_queue.put(('chunk', f"\n\n❌ Ошибка: {str(e)}"))
                self.message_queue.put(('response_done',))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def clear_chat(self):
        """Очистка чата"""
        result = messagebox.askyesno("Очистка чата", "Очистить историю чата?")
        if result:
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.delete('1.0', tk.END)
            self.chat_text.config(state=tk.DISABLED)
            if self.agent:
                self.agent.clear_history()
    
    def save_history(self):
        """Сохранение истории"""
        if self.agent and self.agent.history:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.agent.history, f, ensure_ascii=False, indent=2)
                    messagebox.showinfo("Успех", f"История сохранена в {filename}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")
        else:
            messagebox.showinfo("Информация", "История пуста")


def main():
    """Главная функция"""
    root = tk.Tk()
    app = CodeAgentGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

