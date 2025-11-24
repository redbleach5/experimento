"""
Веб-интерфейс для AI Code Agent
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import asyncio
from agent import CodeAgent
import uvicorn

app = FastAPI(title="AI Code Agent")
templates = Jinja2Templates(directory="templates")

# Инициализация агента
agent = None


@app.on_event("startup")
async def startup():
    """Инициализация при запуске"""
    global agent
    agent = CodeAgent()
    print("🤖 AI Code Agent запущен!")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat")
async def chat(request: Request):
    """API endpoint для чата"""
    data = await request.json()
    prompt = data.get("prompt", "")
    stream = data.get("stream", True)
    
    if not prompt:
        return {"error": "Промпт не может быть пустым"}
    
    async def generate():
        """Асинхронная генерация ответа"""
        for chunk in agent.ask(prompt, stream=stream):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
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
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "chat":
                prompt = message.get("prompt", "")
                
                # Отправляем ответ по частям
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
            
            elif message.get("type") == "clear":
                agent.clear_history()
                await websocket.send_json({"type": "cleared"})
    
    except WebSocketDisconnect:
        print("Клиент отключился")


@app.get("/api/health")
async def health():
    """Проверка здоровья сервиса"""
    return {
        "status": "ok",
        "model": agent.model_name if agent else None,
        "provider": agent.provider if agent else None
    }


def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Запуск веб-сервера"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import sys
    
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    
    run_server(host, port)

