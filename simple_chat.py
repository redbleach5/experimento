"""
Простой чат для тестирования
"""

import sys
import os

# Устанавливаем UTF-8
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')

from agent import CodeAgent
import time

print("\n" + "=" * 70)
print("ПРОСТОЙ ЧАТ С МОДЕЛЬЮ")
print("=" * 70)
print()

try:
    print("[*] Инициализация...")
    agent = CodeAgent()
    print(f"[OK] Готов! Модель: {agent.model_name}")
    print()
    
    print("Введите 'exit' для выхода")
    print("Введите 'test' для тестового запроса про воздушные шарики")
    print()
    
    while True:
        try:
            user_input = input("Вы: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("До свидания!")
                break
            
            if user_input.lower() == 'test':
                user_input = "Расскажи интересные факты про воздушные шарики. Ответь на русском языке."
            
            print("\nAI: ", end='', flush=True)
            
            response = ""
            for chunk in agent.ask(user_input, stream=True):
                if "Ошибка" in chunk or "502" in chunk:
                    if len(response) == 0:
                        print(f"\n[ERROR] {chunk}")
                        break
                else:
                    response += chunk
                    print(chunk, end='', flush=True)
            
            print("\n")
            
        except KeyboardInterrupt:
            print("\n\nПрервано. Введите 'exit' для выхода.")
        except EOFError:
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")

except Exception as e:
    print(f"[ERROR] Ошибка: {e}")
    import traceback
    traceback.print_exc()
    input("\nНажмите Enter для выхода...")

