"""
Прямая проверка LM Studio с детальным выводом
"""

import requests
import json

print("Проверка LM Studio API...")
print()

base_url = "http://127.0.0.1:1234"

# Проверяем /v1/models
try:
    print(f"GET {base_url}/v1/models")
    response = requests.get(f"{base_url}/v1/models", timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(list(response.headers.items())[:3])}")
    print(f"Content length: {len(response.content)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
    elif response.status_code == 502:
        print("502 Bad Gateway - сервер не может обработать запрос")
        if response.content:
            print(f"Response body: {response.content[:200]}")
except Exception as e:
    print(f"Error: {e}")

print()

# Проверяем chat/completions
try:
    print(f"POST {base_url}/v1/chat/completions")
    payload = {
        "model": "qwen3-30b-a3b-instruct-2507",
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 5
    }
    response = requests.post(
        f"{base_url}/v1/chat/completions",
        json=payload,
        timeout=60
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    elif response.status_code == 502:
        print("502 Bad Gateway")
        print(f"Content: {response.content[:200]}")
except Exception as e:
    print(f"Error: {e}")

