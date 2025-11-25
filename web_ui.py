"""
Веб-интерфейс для AI Code Agent
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from agent import CodeAgent
import uvicorn
from pathlib import Path
import os
import yaml
from ide_components import FileBrowser

# Инициализация агента
agent = None
agent_error = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler для инициализации и очистки"""
    # Startup
    global agent, agent_error
    try:
        agent = CodeAgent()
        agent_error = None
        print("🤖 AI Code Agent запущен!")
    except Exception as e:
        agent_error = str(e)
        print(f"❌ Ошибка инициализации агента: {e}")
        print("⚠ Приложение запущено, но агент недоступен")
    yield
    # Shutdown (если нужно что-то очистить)


app = FastAPI(title="AI Code Agent", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

# Подключение статических файлов
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/ide", response_class=HTMLResponse)
async def ide(request: Request):
    """IDE страница"""
    return templates.TemplateResponse("ide.html", {"request": request})


@app.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    """Страница настроек"""
    return templates.TemplateResponse("settings.html", {"request": request})


@app.post("/api/chat")
async def chat(request: Request):
    """API endpoint для чата"""
    global agent, agent_error
    
    if agent is None:
        return {"error": f"Агент не инициализирован: {agent_error or 'Неизвестная ошибка'}"}
    
    data = await request.json()
    prompt = data.get("prompt", "")
    stream = data.get("stream", True)
    
    if not prompt:
        return {"error": "Промпт не может быть пустым"}
    
    async def generate():
        """Асинхронная генерация ответа"""
        try:
            for chunk in agent.ask(prompt, stream=stream):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для реального времени"""
    global agent, agent_error
    
    await websocket.accept()
    
    if agent is None:
        await websocket.send_json({
            "type": "error",
            "content": f"Агент не инициализирован: {agent_error or 'Неизвестная ошибка'}"
        })
        await websocket.close()
        return
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "chat":
                prompt = message.get("prompt", "")
                
                if not prompt:
                    await websocket.send_json({
                        "type": "error",
                        "content": "Промпт не может быть пустым"
                    })
                    continue
                
                # Отправляем ответ по частям
                try:
                    full_response = ""
                    for chunk in agent.ask(prompt, stream=True):
                        full_response += chunk
                        await websocket.send_json({
                            "type": "chunk",
                            "content": chunk
                        })
                    
                    await websocket.send_json({
                        "type": "done",
                        "content": full_response
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "content": f"Ошибка генерации: {str(e)}"
                    })
            
            elif message.get("type") == "clear":
                if agent:
                    agent.clear_history()
                await websocket.send_json({"type": "cleared"})
    
    except WebSocketDisconnect:
        print("Клиент отключился")
    except Exception as e:
        print(f"Ошибка WebSocket: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "content": f"Ошибка: {str(e)}"
            })
        except:
            pass


@app.get("/api/health")
async def health():
    """Проверка здоровья сервиса"""
    global agent, agent_error
    return {
        "status": "ok" if agent else "error",
        "model": agent.model_name if agent else None,
        "provider": agent.provider if agent else None,
        "error": agent_error
    }


# ========== IDE API эндпоинты ==========

@app.get("/api/files/list")
async def list_files(path: str = "."):
    """Список файлов в директории"""
    try:
        full_path = Path(path).resolve()
        if not full_path.exists() or not full_path.is_dir():
            return {"error": "Директория не найдена"}
        
        files = []
        dirs = []
        
        for item in sorted(full_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules', '.git']:
                continue
            
            info = {
                "name": item.name,
                "path": str(item.relative_to(full_path)),
                "full_path": str(item),
                "type": "directory" if item.is_dir() else "file"
            }
            
            if item.is_file():
                info["size"] = item.stat().st_size
                files.append(info)
            else:
                dirs.append(info)
        
        return {"directories": dirs, "files": files, "current_path": str(full_path)}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/files/tree")
async def get_file_tree(root_path: str = ".", max_depth: int = 5):
    """Возвращает дерево файлов и папок"""
    try:
        full_path = Path(root_path).resolve()
        if not full_path.exists():
            return {"error": "Путь не найден"}
        
        tree = FileBrowser.get_file_tree(str(full_path), max_depth=max_depth)
        return {
            "tree": tree,
            "root_path": str(full_path)
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/files/read")
async def read_file(file_path: str):
    """Чтение файла"""
    try:
        path = Path(file_path).resolve()
        if not path.exists() or not path.is_file():
            return {"error": "Файл не найден"}
        
        content = FileBrowser.get_file_content(str(path))
        if content is None:
            return {"error": "Не удалось прочитать файл"}
        
        return {
            "content": content,
            "path": str(path),
            "language": FileBrowser.detect_language(str(path))
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/files/write")
async def write_file(request: Request):
    """Сохранение файла"""
    try:
        data = await request.json()
        file_path = data.get("path")
        content = data.get("content", "")
        
        if not file_path:
            return {"error": "Путь к файлу не указан"}
        
        if FileBrowser.save_file(file_path, content):
            return {"success": True, "path": file_path}
        else:
            return {"error": "Не удалось сохранить файл"}
    except Exception as e:
        return {"error": str(e)}


# ========== Settings API эндпоинты ==========

@app.get("/api/settings")
async def get_settings():
    """Получение текущей конфигурации"""
    try:
        config_path = Path("config.yaml")
        if not config_path.exists():
            return {"error": "Файл config.yaml не найден"}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        
        return {"success": True, "config": config}
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/settings")
async def save_settings(request: Request):
    """Сохранение конфигурации"""
    try:
        data = await request.json()
        config = data.get("config", {})
        
        if not config:
            return {"error": "Конфигурация не предоставлена"}
        
        config_path = Path("config.yaml")
        
        # Создаем резервную копию
        if config_path.exists():
            backup_path = config_path.with_suffix('.yaml.backup')
            with open(config_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)
        
        # Сохраняем новую конфигурацию
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        # Перезагружаем агента с новой конфигурацией
        global agent, agent_error
        try:
            agent = CodeAgent()
            agent_error = None
        except Exception as e:
            agent_error = str(e)
            return {
                "success": True,
                "warning": f"Конфигурация сохранена, но не удалось перезагрузить агента: {str(e)}"
            }
        
        return {"success": True, "message": "Настройки успешно сохранены и применены"}
    except Exception as e:
        return {"error": str(e)}


def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Запуск веб-сервера"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import sys
    
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    
    run_server(host, port)

