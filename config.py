from dataclasses import dataclass
import os

@dataclass
class Settings:
    bot_token: str
    webhook_secret: str
    base_url: str
    horde_key: str | None
    daily_free_limit: int

def load_settings() -> Settings:
    from dotenv import load_dotenv
    load_dotenv()
    return Settings(
        bot_token=os.getenv("BOT_TOKEN","").strip(),
        webhook_secret=os.getenv("WEBHOOK_SECRET","").strip(),
        base_url=os.getenv("BASE_URL","").strip(),
        horde_key=(os.getenv("HORDE_API_KEY") or None),
        daily_free_limit=int(os.getenv("DAILY_FREE_LIMIT","5"))
    )
