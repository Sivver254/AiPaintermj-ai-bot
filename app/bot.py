from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hbold
from .horde import HordeClient
from .config import load_settings
from .keyboards import main_kb, styles_kb
import base64, re
from io import BytesIO
from PIL import Image

router = Router()
settings = load_settings()
horde = HordeClient(api_key=settings.horde_key)

HELP = (
    "Это бесплатный генератор картинок @AiPaintermj_bot 🎨\n\n"
    "Как пользоваться:\n"
    "• Нажми «🎨 Создать картинку» и напиши промпт\n"
    "• Или команды: /imagine <текст>, /realism <текст>, /anime <текст>, /pixel <текст>\n"
    "• Параметры (необязательно): --w 768 --h 512 --steps 30 --cfg 7\n"
    "Подсказка: чем конкретнее описание, тем лучше результат."
)

STYLE_PROMPTS = {
    "realism": "highly detailed realistic photography, natural lighting, cinematic, 50mm lens",
    "anime":   "anime style, vibrant colors, clean lineart, studio quality, highly detailed",
    "pixel":   "pixel art, 16-bit retro game style, crisp pixels, limited color palette",
}

def parse_params(text: str):
    width = int(re.search(r"--w\s+(\d+)", text).group(1)) if re.search(r"--w\s+(\d+)", text) else 768
    height = int(re.search(r"--h\s+(\d+)", text).group(1)) if re.search(r"--h\s+(\d+)", text) else 768
    steps = int(re.search(r"--steps\s+(\d+)", text).group(1)) if re.search(r"--steps\s+(\d+)", text) else 28
    cfg = float(re.search(r"--cfg\s+([\d\.]+)", text).group(1)) if re.search(r"--cfg\s+([\d\.]+)", text) else 7.0
    clean = re.sub(r"--(w|h|steps|cfg)\s+\S+", "", text).strip()
    return clean, width, height, steps, cfg

async def _generate_and_send(m: Message, prompt: str, style_key: str | None):
    prefix = STYLE_PROMPTS.get(style_key or "", "")
    final_prompt = f"{prefix}. {prompt}".strip(". ")

    await m.answer("⏳ Генерация… (на бесплатном кластере может занять ~полминуты)", reply_markup=main_kb())
    try:
        req_id = await horde.generate(final_prompt)
        status = await horde.wait_for_result(req_id)
        gens = status.get("generations") or status.get("images") or []
        if not gens:
            await m.answer("Не получилось получить изображение. Попробуй ещё раз или измени промпт.", reply_markup=main_kb())
            return

        b64 = gens[0].get("img") if isinstance(gens[0], dict) else gens[0]
        img_bytes = base64.b64decode(b64)
        im = Image.open(BytesIO(img_bytes)).convert("RGB")
        out = BytesIO(); im.save(out, format="JPEG", quality=92); out.seek(0)

        cap_style = style_key or "без стиля"
        await m.answer_photo(out, caption=f"Стиль: {cap_style}\nЗапрос: {prompt}", reply_markup=main_kb())
    except Exception as e:
        await m.answer(f"Ошибка: {e}", reply_markup=main_kb())

@router.message(CommandStart())
async def start(m: Message):
    await m.answer(f"Привет, {hbold(m.from_user.full_name)}!\n{HELP}", reply_markup=main_kb())

@router.message(Command("help"))
async def help_cmd(m: Message):
    await m.answer(HELP, reply_markup=main_kb())

@router.message(F.text == "ℹ️ Помощь")
async def help_btn(m: Message):
    await m.answer(HELP, reply_markup=main_kb())

@router.message(F.text == "🧭 Выбрать стиль")
async def pick_style(m: Message):
    await m.answer("Выберите стиль:", reply_markup=styles_kb())

@router.message(F.text == "⬅️ Назад")
async def back_to_main(m: Message):
    await m.answer("Готово. Напиши промпт или выбери действие.", reply_markup=main_kb())

@router.message(F.text == "🎨 Создать картинку")
async def create_btn(m: Message):
    await m.answer("Напиши описание картинки (промпт). Например: «кот в космосе на фоне туманности»", reply_markup=main_kb())

@router.message(Command("imagine"))
async def imagine(m: Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        await m.answer("Пример: /imagine кот в космосе --w 768 --h 512", reply_markup=main_kb())
        return
    text, w, h, steps, cfg = parse_params(parts[1])
    await _generate_and_send(m, text, style_key=None)

@router.message(Command("realism"))
async def realism(m: Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        await m.answer("Пример: /realism закат над океаном", reply_markup=main_kb())
        return
    text, *_ = parse_params(parts[1])
    await _generate_and_send(m, text, style_key="realism")

@router.message(Command("anime"))
async def anime(m: Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        await m.answer("Пример: /anime герой с синей аурой", reply_markup=main_kb())
        return
    text, *_ = parse_params(parts[1])
    await _generate_and_send(m, text, style_key="anime")

@router.message(Command("pixel"))
async def pixel(m: Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        await m.answer("Пример: /pixel рыцарь в подземелье", reply_markup=main_kb())
        return
    text, *_ = parse_params(parts[1])
    await _generate_and_send(m, text, style_key="pixel")

@router.message(F.text & ~F.text.startswith("/"))
async def free_prompt(m: Message):
    await _generate_and_send(m, m.text.strip(), style_key="realism")
