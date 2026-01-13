import asyncio
import nest_asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN
from quiz_data import quiz_data
from database import init_db, save_result, get_result

nest_asyncio.apply()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_states = {}

def get_keyboard(question_index):
    buttons = []
    for i, option in enumerate(quiz_data[question_index]["options"]):
        buttons.append(
            [InlineKeyboardButton(text=option, callback_data=str(i))]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer(
        "Привет! Нажми /quiz чтобы начать квиз.\n/stats — статистика"
    )

@dp.message(F.text == "/quiz")
async def quiz(message: types.Message):
    user_states[message.from_user.id] = {"q": 0, "score": 0}
    await message.answer(
        quiz_data[0]["question"],
        reply_markup=get_keyboard(0)
    )

@dp.message(F.text == "/stats")
async def stats(message: types.Message):
    result = await get_result(message.from_user.id)
    if result is None:
        await message.answer("Ты ещё не проходил квиз.")
    else:
        await message.answer(f"Твой последний результат: {result}/10")

@dp.callback_query()
async def answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    state = user_states.get(user_id)

    if not state:
        await callback.answer()
        return

    q = state["q"]
    selected = int(callback.data)
    correct = quiz_data[q]["correct"]

    await callback.message.edit_reply_markup()

    await callback.message.answer(
        f"Ты выбрал: {quiz_data[q]['options'][selected]}"
    )

    if selected == correct:
        state["score"] += 1
        await callback.message.answer("Верно!")
    else:
        await callback.message.answer("Неверно")

    state["q"] += 1

    if state["q"] >= len(quiz_data):
        await save_result(user_id, state["score"])
        await callback.message.answer(
            f"Квиз завершён! Результат: {state['score']}/10"
        )
        user_states.pop(user_id)
    else:
        await callback.message.answer(
            quiz_data[state["q"]]["question"],
            reply_markup=get_keyboard(state["q"])
        )

    await callback.answer()

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
