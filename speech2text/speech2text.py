import os
import tempfile

import speech_recognition as sr
from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dotenv import load_dotenv
from pydub import AudioSegment

import keyboard
from fsm import FSM

load_dotenv()

router = Router()
FILES_DIR = "speech2text/audio_files"


def convert_to_wav(audio_path: str) -> str:
    """Convert any audio file to WAV format"""
    sound = AudioSegment.from_file(audio_path)
    wav_path = audio_path + ".wav"
    sound.export(wav_path, format="wav")
    return wav_path


def recognize(audio_path: str) -> str:
    recognizer = sr.Recognizer()

    try:
        if not audio_path.lower().endswith(".wav"):
            audio_path = convert_to_wav(audio_path)

        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="en-US")
            return text

    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Error with the speech recognition service; {e}"
    except Exception as e:
        return f"Error processing audio: {str(e)}"
    finally:
        if audio_path.lower().endswith(".wav") and os.path.exists(audio_path):
            try:
                os.unlink(audio_path)
            except:
                pass


@router.message(Command("speech_to_text🎤"))
async def set_state_sending_audio(message: Message, state: FSMContext):
    await state.set_state(FSM.sending_audio)
    await message.answer("Send your audio:", reply_markup=keyboard.back_key)


@router.message(FSM.sending_audio)
async def speech_to_text(message: Message, bot: Bot):
    try:
        if message.audio:
            audio_id = message.audio.file_id
        elif message.document:
            audio_id = message.document.file_id
        elif message.voice:
            audio_id = message.voice.file_id
        else:
            await message.answer("Please send an audio file or voice message.")
            return

        audio_info = await bot.get_file(audio_id)

        with tempfile.NamedTemporaryFile(delete=False) as temp_audio:
            audio_path = temp_audio.name
            await bot.download_file(
                file_path=audio_info.file_path, destination=audio_path
            )

        try:
            recognized_text = recognize(audio_path)
            await message.answer(
                recognized_text if recognized_text else "No speech detected"
            )
        finally:
            try:
                os.unlink(audio_path)
            except:
                pass

    except Exception as e:
        print(f"Error: {e}")
        await message.answer(
            "Error processing your audio. Please try again with a different format or shorter message."
        )
