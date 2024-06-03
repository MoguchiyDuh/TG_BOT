from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import pytesseract
import os
from time import localtime, strftime
import json
from fsm import FSM
import keyboard


with open("config.json", "r") as file:
    config = json.load(file)


router = Router()
LANG = config["PYTESSERACT_LANG"]
IMAGES_DIR = "image2text/images"


def parse(image_path: str) -> str:
    return pytesseract.image_to_string(image_path, lang=LANG)


@router.message(Command("text_from_image🖼"))
async def set_state_sending_image(message: Message, state: FSMContext):
    await state.set_state(FSM.sending_image)
    await message.answer("Waiting your image:", reply_markup=keyboard.back_key)


@router.message(FSM.sending_image)
async def image_to_text(message: Message, bot: Bot):
    global IMAGES_DIR
    try:
        if message.photo != None:
            image_id = message.photo[-1].file_id
        elif message.document != None:
            image_id = message.document.file_id

        image_info = await bot.get_file(image_id)
        extension = os.path.splitext(image_info.file_path)[1]
        timecode = strftime("%Y.%m.%d-%H.%M.%S", localtime())
        image_path = f"{IMAGES_DIR}/{image_id}-{timecode}-{extension}"
        await bot.download_file(file_path=image_info.file_path, destination=image_path)
        result = parse(image_path)
        if result != "":
            await message.answer(result)
        else:
            await message.answer("Empty")
        # os.remove(image_path)
    except Exception:
        await message.answer("TRY AGAIN❗:")
