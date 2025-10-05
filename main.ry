from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from .config import load_settings
from .bot import router as bot_router

settings = load_settings()
bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(bot_router)

app = FastAPI()

def _webhook_path():
    return f"/tg/webhook/{settings.webhook_secret}"

@app.on_event("startup")
async def on_startup():
    # Если BASE_URL заполнен — регистрируем вебхук автоматически
    if settings.base_url:
        await bot.set_webhook(url=f"{settings.base_url}{_webhook_path()}", drop_pending_updates=True)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

@app.post(_webhook_path())
async def telegram_webhook(request: Request):
    data = await request.json()
    await dp.feed_webhook_update(bot, data)
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "ok", "bot": "AiPaintermj_bot"}
