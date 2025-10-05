# app/main.py
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher

from .config import load_settings
from .bot import router as bot_router

# Загружаем переменные окружения
settings = load_settings()

# Создаём бота БЕЗ parse_mode
bot = Bot(token=settings.bot_token)

# Настраиваем диспетчер и подключаем роутеры
dp = Dispatcher()
dp.include_router(bot_router)

# FastAPI приложение
app = FastAPI()

def _webhook_path() -> str:
    # Путь для вебхука. Должен совпадать с URL при setWebhook
    return f"/tg/webhook/{settings.webhook_secret}"

@app.on_event("startup")
async def on_startup():
    # Если BASE_URL указан — ставим вебхук автоматически при старте
    if settings.base_url:
        await bot.set_webhook(
            url=f"{settings.base_url}{_webhook_path()}",
            drop_pending_updates=True
        )

@app.on_event("shutdown")
async def on_shutdown():
    # Чистим вебхук при остановке
    await bot.delete_webhook()

# Обработчик вебхука от Telegram
@app.post(_webhook_path())
async def telegram_webhook(request: Request):
    data = await request.json()
    await dp.feed_webhook_update(bot, data)
    return {"ok": True}

# Health-check (Render пингует /)
@app.get("/")
async def root():
    return {"status": "ok", "bot": "AiPaintermj_bot"}
