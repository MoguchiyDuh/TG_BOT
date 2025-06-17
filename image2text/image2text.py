import contextlib
import os
import tempfile

import pytesseract
from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dotenv import load_dotenv

import keyboard
from fsm import FSM

load_dotenv()

router = Router()
PYTESSERACT_LANG = os.getenv("PYTESSERACT_LANG", "eng")


def extract_text(image_path: str) -> str:
    """Extract text from image using pytesseract"""
    try:
        text = pytesseract.image_to_string(image_path, lang=PYTESSERACT_LANG).strip()
        return text if text else "No text found in image"
    except Exception as e:
        return f"Error processing image: {str(e)}"


@router.message(Command("text_from_image🖼"))
async def handle_image_command(message: Message, state: FSMContext) -> None:
    """Handle image to text command"""
    await state.set_state(FSM.sending_image)
    await message.answer("Send your image:", reply_markup=keyboard.back_key)


@router.message(FSM.sending_image)
async def process_image_message(message: Message, bot: Bot) -> None:
    """Process incoming image message"""
    if not any([message.photo, message.document]):
        await message.answer("Please send an image file or photo.")
        return

    try:
        file_id = (
            message.photo[-1].file_id if message.photo else message.document.file_id
        )
        file_info = await bot.get_file(file_id)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            await bot.download_file(file_info.file_path, temp_file.name)

            try:
                result = extract_text(temp_file.name)
                await message.answer(result)
            finally:
                with contextlib.suppress(Exception):
                    os.unlink(temp_file.name)

    except Exception as e:
        print(f"Image processing error: {e}")
        await message.answer(
            "Error processing image. Please try again with a different file."
        )
