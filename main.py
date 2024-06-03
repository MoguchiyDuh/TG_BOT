from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import asyncio
import json
import keyboard
from image2text import image2text
from speech2text import speech2text
from text2speech import text2speech


with open("config.json", "r") as file:
    config: dict = json.load(file)

if config["BOT_TOKEN"] == "None":
    raise Exception(
        'Token is not found, please set "BOT_TOKEN" in config.json. To see more, read README.md'
    )

BOT_TOKEN = config["BOT_TOKEN"]
bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(f"Hello, {message.from_user.full_name}❗", reply_markup=keyboard.create_reply_keyboard())  # type: ignore


@dp.message(Command("status❓"))
async def status(message: Message):
    await message.answer("✅Working✅")


@dp.message(Command("back🔙"))
async def cancel(message: Message, state: FSMContext):
    await message.answer("Back🔙", reply_markup=keyboard.create_reply_keyboard())
    await state.clear()


async def main():
    print("Started")
    dp.include_routers(image2text.router, speech2text.router, text2speech.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("ctrl+C")
