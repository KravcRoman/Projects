import asyncio
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import enum

# URL подключения к базе данных PostgreSQL (не забудьте настроить переменные окружения в production)
DATABASE_URL = "postgresql+asyncpg://user:password@db:5432/dbname"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

# Enum для типа чата
class ChatTypeEnum(enum.Enum):
    personal = "personal"
    group = "group"

# Модели БД
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(Enum(ChatTypeEnum), nullable=False)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)

# FastAPI приложение
app = FastAPI(title="Chat App", description="Мини-приложение для чата с WebSocket", version="1.0")

# Зависимость для получения сессии БД
async def get_db():
    async with async_session() as session:
        yield session

# Менеджер WebSocket-соединений для конкретных чатов
class ConnectionManager:
    def __init__(self):
        # Хранит активные подключения: ключ — chat_id, значение — список WebSocket
        self.active_connections: dict[int, List[WebSocket]] = {}

    async def connect(self, chat_id: int, websocket: WebSocket):
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []
        self.active_connections[chat_id].append(websocket)

    def disconnect(self, chat_id: int, websocket: WebSocket):
        if chat_id in self.active_connections:
            self.active_connections[chat_id].remove(websocket)
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

    async def broadcast(self, chat_id: int, message: dict):
        if chat_id in self.active_connections:
            for connection in self.active_connections[chat_id]:
                await connection.send_json(message)

manager = ConnectionManager()

# WebSocket-эндпоинт для общения в чате
@app.websocket("/ws/{chat_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    await manager.connect(chat_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            text_message = data.get("text")
            if not text_message:
                continue

            # Здесь можно добавить дополнительную проверку для предотвращения дублирования
            # (например, проверка по уникальному idempotency-токену или похожему механизму).

            new_message = Message(
                chat_id=chat_id,
                sender_id=user_id,
                text=text_message,
                timestamp=datetime.utcnow()
            )
            db.add(new_message)
            await db.commit()
            await db.refresh(new_message)

            message_data = {
                "id": new_message.id,
                "chat_id": new_message.chat_id,
                "sender_id": new_message.sender_id,
                "text": new_message.text,
                "timestamp": new_message.timestamp.isoformat(),
                "read": new_message.read,
            }
            # Отправляем сообщение всем участникам чата
            await manager.broadcast(chat_id, message_data)
    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)

# REST-эндпоинт для получения истории сообщений чата
@app.get("/history/{chat_id}")
async def get_chat_history(chat_id: int, limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    # Используем текстовый запрос для простоты; в production лучше использовать ORM-запросы
    result = await db.execute(
        text("SELECT id, chat_id, sender_id, text, timestamp, read FROM messages "
             "WHERE chat_id = :chat_id ORDER BY timestamp ASC LIMIT :limit OFFSET :offset"),
        {"chat_id": chat_id, "limit": limit, "offset": offset},
    )
    messages = result.fetchall()
    return [
        {
            "id": m.id,
            "chat_id": m.chat_id,
            "sender_id": m.sender_id,
            "text": m.text,
            "timestamp": m.timestamp.isoformat(),
            "read": m.read,
        }
        for m in messages
    ]

# Простой HTML-клиент для тестирования WebSocket (демо)
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Чат</title>
    </head>
    <body>
        <h1>WebSocket Чат</h1>
        <form id="form">
            <input type="text" id="messageText" autocomplete="off" placeholder="Введите сообщение"/>
            <button>Отправить</button>
        </form>
        <ul id="messages"></ul>
        <script>
            const chat_id = prompt("Введите chat_id:");
            const user_id = prompt("Введите ваш user_id:");
            const ws = new WebSocket(`ws://localhost:8000/ws/${chat_id}/${user_id}`);
            ws.onmessage = function(event) {
                const messages = document.getElementById('messages');
                const message = document.createElement('li');
                const data = JSON.parse(event.data);
                message.innerText = data.sender_id + ": " + data.text;
                messages.appendChild(message);
            };
            document.getElementById('form').onsubmit = function(event) {
                event.preventDefault();
                const input = document.getElementById("messageText");
                ws.send(JSON.stringify({text: input.value}));
                input.value = '';
            };
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

# Создание таблиц в БД при запуске приложения (демо)
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
