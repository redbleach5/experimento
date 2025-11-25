/**
 * WebSocket клиент для AI Code Agent
 */

class WebSocketClient {
    constructor(url, callbacks = {}) {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.callbacks = {
            onOpen: callbacks.onOpen || (() => {}),
            onMessage: callbacks.onMessage || (() => {}),
            onError: callbacks.onError || (() => {}),
            onClose: callbacks.onClose || (() => {}),
            onReconnect: callbacks.onReconnect || (() => {})
        };
    }

    connect() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}${this.url}`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                this.reconnectAttempts = 0;
                this.callbacks.onOpen();
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.callbacks.onMessage(data);
                } catch (e) {
                    console.error('Ошибка парсинга сообщения:', e);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket ошибка:', error);
                this.callbacks.onError(error);
            };
            
            this.ws.onclose = () => {
                this.callbacks.onClose();
                this.attemptReconnect();
            };
        } catch (e) {
            console.error('Ошибка подключения WebSocket:', e);
            this.attemptReconnect();
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            this.callbacks.onReconnect(this.reconnectAttempts);
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
        }
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
            return true;
        }
        return false;
    }

    close() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

// Экспорт
window.WebSocketClient = WebSocketClient;

