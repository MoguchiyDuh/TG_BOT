from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import os
from dotenv import load_dotenv
from time import localtime, strftime
import whisper
from fsm import FSM
import keyboard


load_dotenv()

router = Router()
FILES_DIR = "speech2text/audio_files"
MODEL = os.getenv("WHISPER_MODEL")

if os.path.isfile(MODEL):
    MODEL = whisper.load_model(MODEL)
else:
    MODEL = whisper.load_model("tiny", download_root="speech2text/model")


def recognize(audio_path: str) -> str:
    global MODEL
    result = MODEL.transcribe(audio_path)
    return result["text"]


@router.message(Command("speech_to_text🎤"))
async def set_state_sending_audio(message: Message, state: FSMContext):
    await state.set_state(FSM.sending_audio)
    await message.answer("Send your audio:", reply_markup=keyboard.back_key)


@router.message(FSM.sending_audio)
async def speech_to_text(message: Message, bot: Bot):
    global FILES_DIR
    try:
        if message.audio != None:
            audio_id = message.audio.file_id
        elif message.document != None:
            audio_id = message.document.file_id
        elif message.voice != None:
            audio_id = message.voice.file_id
        audio_info = await bot.get_file(audio_id)
        extension = os.path.splitext(audio_info.file_path)[1]
        timecode = strftime("%Y.%m.%d-%H.%M.%S", localtime())
        if not os.path.isdir(f"{FILES_DIR}/{message.from_user.id}"):
            os.mkdir(f"{FILES_DIR}/{message.from_user.id}")
        audio_path = f"{FILES_DIR}/{message.from_user.id}/{timecode}{extension}"
        await bot.download_file(file_path=audio_info.file_path, destination=audio_path)
        await message.answer(recognize(audio_path))
        # os.remove(audio_path)
    except Exception as e:
        print(e)
        await message.answer("SEND YOUR AUDIO❗:")
