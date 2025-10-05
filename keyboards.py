from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎨 Создать картинку")],
            [KeyboardButton(text="🧭 Выбрать стиль"), KeyboardButton(text="ℹ️ Помощь")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Напишите промпт или выберите действие"
    )

def styles_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📷 Реализм"), KeyboardButton(text="🌸 Аниме")],
            [KeyboardButton(text="🧩 Пиксель-арт"), KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите стиль"
    )
