"""
Улучшенный CLI интерфейс для AI Code Agent
"""

import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from agent import CodeAgent
import os
from pathlib import Path

console = Console()

# Стиль для prompt_toolkit
style = Style.from_dict({
    'prompt': 'fg:#667eea bold',
    'input': 'fg:#ffffff',
})

class CodeCompleter(Completer):
    """Автодополнение для команд"""
    def get_completions(self, document, complete_event):
        commands = ['exit', 'quit', 'clear', 'help', 'history', 'save', 'load']
        word = document.get_word_before_cursor()
        for cmd in commands:
            if cmd.startswith(word):
                yield Completion(cmd, start_position=-len(word))


def print_welcome():
    """Приветственное сообщение"""
    welcome_text = """
[bold cyan]╔═══════════════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║                                                           ║[/bold cyan]
[bold cyan]║           🤖 AI Code Agent - Локальный помощник          ║[/bold cyan]
[bold cyan]║                                                           ║[/bold cyan]
[bold cyan]╚═══════════════════════════════════════════════════════════╝[/bold cyan]

[dim]Введите ваш запрос о коде. Доступные команды:[/dim]
  • [yellow]help[/yellow] - показать справку
  • [yellow]clear[/yellow] - очистить историю
  • [yellow]exit[/yellow] - выйти
  • [yellow]history[/yellow] - показать историю
  • [yellow]save[/yellow] - сохранить текущую сессию
  • [yellow]load[/yellow] - загрузить сессию

[dim]Примеры запросов:[/dim]
  • "Напиши функцию для сортировки массива на Python"
  • "Объясни разницу между async и await в JavaScript"
  • "Создай REST API на FastAPI с аутентификацией"

"""
    console.print(Panel(welcome_text, border_style="cyan", padding=(1, 2)))


def print_help():
    """Справка по командам"""
    help_text = """
[bold]Доступные команды:[/bold]

  [yellow]help[/yellow]          - Показать эту справку
  [yellow]clear[/yellow]         - Очистить историю диалога
  [yellow]exit[/yellow] / [yellow]quit[/yellow]  - Выйти из программы
  [yellow]history[/yellow]      - Показать последние сообщения
  [yellow]save[/yellow]          - Сохранить текущую сессию
  [yellow]load <file>[/yellow]   - Загрузить сессию из файла

[bold]Советы:[/bold]
  • Используйте Shift+Enter для многострочного ввода
  • Будьте конкретны в запросах для лучших результатов
  • Указывайте язык программирования в запросах
"""
    console.print(Panel(help_text, title="[cyan]Справка[/cyan]", border_style="cyan"))


def format_code_in_response(text: str) -> str:
    """Форматирование кода в ответе"""
    # Простое определение блоков кода
    lines = text.split('\n')
    result = []
    in_code_block = False
    code_block = []
    language = ''
    
    for line in lines:
        if line.strip().startswith('```'):
            if in_code_block:
                # Закрываем блок кода
                if code_block:
                    code_text = '\n'.join(code_block)
                    syntax = Syntax(code_text, language or 'text', theme='monokai', line_numbers=True)
                    result.append(syntax)
                    code_block = []
                in_code_block = False
                language = ''
            else:
                # Открываем блок кода
                language = line.strip()[3:].strip() or 'text'
                in_code_block = True
        elif in_code_block:
            code_block.append(line)
        else:
            result.append(line)
    
    # Если остался незакрытый блок
    if code_block:
        code_text = '\n'.join(code_block)
        syntax = Syntax(code_text, language or 'text', theme='monokai', line_numbers=True)
        result.append(syntax)
    
    return '\n'.join(str(r) for r in result) if result else text


def main():
    """Основная функция CLI"""
    # Создаем директорию для истории
    history_dir = Path.home() / '.ai_agent'
    history_dir.mkdir(exist_ok=True)
    history_file = history_dir / 'history.txt'
    
    # Инициализация агента
    try:
        agent = CodeAgent()
    except Exception as e:
        console.print(f"[red]Ошибка инициализации агента: {e}[/red]")
        console.print("[yellow]Убедитесь, что Ollama установлен и запущен[/yellow]")
        return
    
    # Создаем сессию prompt_toolkit
    session = PromptSession(
        history=FileHistory(str(history_file)),
        auto_suggest=AutoSuggestFromHistory(),
        completer=CodeCompleter(),
        style=style,
        multiline=True,
    )
    
    print_welcome()
    
    while True:
        try:
            # Получаем ввод пользователя
            user_input = session.prompt(
                "\n[bold cyan]💬 Вы:[/bold cyan] ",
                style=style
            ).strip()
            
            if not user_input:
                continue
            
            # Обработка команд
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("\n[yellow]До свидания![/yellow]")
                break
            
            elif user_input.lower() == 'help':
                print_help()
                continue
            
            elif user_input.lower() == 'clear':
                agent.clear_history()
                console.print("[green]✓ История очищена[/green]")
                continue
            
            elif user_input.lower() == 'history':
                if agent.history:
                    console.print("\n[bold]История диалога:[/bold]")
                    for i, msg in enumerate(agent.history[-5:], 1):  # Последние 5 сообщений
                        role = "Вы" if msg['role'] == 'user' else "AI"
                        console.print(f"[dim]{i}. {role}:[/dim] {msg['content'][:100]}...")
                else:
                    console.print("[yellow]История пуста[/yellow]")
                continue
            
            elif user_input.lower() == 'save':
                agent._save_history()
                console.print(f"[green]✓ История сохранена в {agent.history_path}[/green]")
                continue
            
            elif user_input.lower().startswith('load '):
                file_path = user_input[5:].strip()
                try:
                    agent.load_history(file_path)
                except Exception as e:
                    console.print(f"[red]Ошибка загрузки: {e}[/red]")
                continue
            
            # Обычный запрос к агенту
            console.print("\n[cyan]🤖 Агент генерирует ответ...[/cyan]\n")
            
            # Собираем ответ
            full_response = ""
            response_parts = []
            
            try:
                for chunk in agent.ask(user_input, stream=True):
                    full_response += chunk
                    response_parts.append(chunk)
                    # Показываем прогресс
                    if len(response_parts) % 10 == 0:  # Каждые 10 чанков
                        console.print(f"[dim]Получено {len(full_response)} символов...[/dim]", end='\r')
                
                console.print()  # Новая строка после прогресса
                
                # Форматируем и выводим ответ
                console.print(Panel(
                    Markdown(full_response),
                    title="[green]AI Agent[/green]",
                    border_style="green",
                    padding=(1, 2)
                ))
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Генерация прервана[/yellow]")
            except Exception as e:
                console.print(f"[red]Ошибка: {e}[/red]")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Прервано пользователем. Введите 'exit' для выхода.[/yellow]")
        except EOFError:
            console.print("\n[yellow]До свидания![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Неожиданная ошибка: {e}[/red]")


if __name__ == "__main__":
    main()

