import os
import tempfile

import torch
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from dotenv import load_dotenv

import keyboard
from fsm import FSM

load_dotenv()

router = Router()
DEFAULT_DIR = "text2speech/model"
LANG = ""
SPEAKER = ""
TTS_MODEL = os.getenv("TTS_MODEL")
MODEL = None


def create_models_dict(directory: str) -> dict:
    res = {}
    for model in os.listdir(directory):
        file_path = os.path.join(directory, model)
        if os.path.isfile(file_path):
            name, extention = os.path.splitext(model)
            if extention == ".pt":
                res[file_path] = name
    return res


if os.listdir(TTS_MODEL):
    TTS_MODELS = create_models_dict(TTS_MODEL)
else:
    torch.hub.download_url_to_file(
        "https://models.silero.ai/models/tts/en/v3_en.pt",
        f"{DEFAULT_DIR}/v3_en.pt",
    )
    TTS_MODELS = create_models_dict(DEFAULT_DIR)


def create_tts_file(model, text: str, speaker: str, sample_rate: int = 48000) -> str:
    """Create a temporary TTS file and return its path"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_path = temp_file.name
        model.save_wav(
            text=text,
            speaker=speaker,
            sample_rate=sample_rate,
            audio_path=temp_path,
        )
    return temp_path


@router.message(Command("text_to_speech💬"))
async def set_state_sending_text(message: Message):
    global TTS_MODELS
    await message.answer(
        "What language do you want to use?",
        reply_markup=keyboard.create_inline_lang_keyboard(TTS_MODELS.values()),
    )


@router.callback_query(keyboard.LANG_Callback.filter(F.lang != None))
async def lang_handler(query: CallbackQuery, callback_data: keyboard.LANG_Callback):
    global MODEL, TTS_MODELS, LANG
    LANG = callback_data.lang
    for model_path, lang in TTS_MODELS.items():
        if lang == LANG:
            break

    MODEL = torch.package.PackageImporter(model_path).load_pickle("tts_models", "model")
    if torch.cuda.is_available():
        print("Using CUDA")
        MODEL.to(torch.device("cuda"))
    else:
        print("CUDA is not available, cpu will be used. To see more, read README.md")
        MODEL.to(torch.device("cpu"))

    speakers_markup = keyboard.create_inline_speakers_keyboard(MODEL.speakers[:-1])
    if type(speakers_markup) == list:
        for markup in speakers_markup:
            await query.message.answer("Choose the speaker:", reply_markup=markup)
    else:
        await query.message.answer(
            "Choose the speaker:",
            reply_markup=speakers_markup,
        )


@router.callback_query(keyboard.SPEAKER_Callback.filter(F.speaker != None))
async def speaker_handler(
    query: CallbackQuery, callback_data: keyboard.SPEAKER_Callback, state: FSMContext
):
    global SPEAKER
    SPEAKER = callback_data.speaker
    await state.set_state(FSM.sending_text)
    await query.message.answer("Enter your text:")


@router.message(FSM.sending_text)
async def tts(message: Message):
    global MODEL, SPEAKER
    if not message.text:
        await message.answer("Please send text for conversion")
        return

    try:
        # Create temporary file
        temp_path = create_tts_file(model=MODEL, text=message.text, speaker=SPEAKER)

        try:
            # Send the audio file
            await message.answer_audio(
                audio=FSInputFile(temp_path), reply_markup=keyboard.back_key
            )
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_path)
            except:
                pass

    except Exception as e:
        print(f"Error in TTS: {e}")
        await message.answer(
            "Error generating speech. The text might be too long or in an unsupported language."
        )
