from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
import os
from dotenv import load_dotenv
from time import localtime, strftime
import torch
from fsm import FSM
import keyboard


load_dotenv()

router = Router()
DEFAULT_DIR = "text2speech/model"
LANG = ""
SPEAKER = ""
SILERO_MODEL = os.getenv("SILERO_MODEL")
MODEL = None
FILES_DIR = "text2speech/tts_audio"


def create_models_dict(directory: str) -> dict:
    res = {}
    for model in os.listdir(directory):
        file_path = os.path.join(directory, model)
        if os.path.isfile(file_path):
            name, extention = os.path.splitext(model)
            if extention == ".pt":
                res[file_path] = name
    return res


if os.listdir(SILERO_MODEL):
    SILERO_MODELS = create_models_dict(SILERO_MODEL)
else:
    torch.hub.download_url_to_file(
        "https://models.silero.ai/models/tts/en/v3_en.pt",
        f"{DEFAULT_DIR}/v3_en.pt",
    )
    SILERO_MODELS = create_models_dict(DEFAULT_DIR)


def create_tts_file(
    model, path: str, text: str, speaker: str, sample_rate: int = 48000
):
    model.save_wav(
        text=text,
        speaker=speaker,
        sample_rate=sample_rate,
        audio_path=path,
    )


@router.message(Command("text_to_speech💬"))
async def set_state_sending_text(message: Message):
    global SILERO_MODELS
    await message.answer(
        "What language do you want to use?",
        reply_markup=keyboard.create_inline_lang_keyboard(SILERO_MODELS.values()),
    )


@router.callback_query(keyboard.LANG_Callback.filter(F.lang != None))
async def lang_handler(query: CallbackQuery, callback_data: keyboard.LANG_Callback):
    global MODEL, SILERO_MODELS
    LANG = callback_data.lang
    for model_path, lang in SILERO_MODELS.items():
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
    global MODEL, FILES_DIR, SPEAKER
    if message.text != None:
        timecode = strftime("%Y.%m.%d-%H.%M.%S", localtime())
        if not os.path.isdir(f"{FILES_DIR}/{message.from_user.id}"):
            os.mkdir(f"{FILES_DIR}/{message.from_user.id}")
        path = f"{FILES_DIR}/{message.from_user.id}/{timecode}.wav"
        try:
            create_tts_file(model=MODEL, path=path, text=message.text, speaker=SPEAKER)
            await message.answer_audio(
                audio=FSInputFile(path), reply_markup=keyboard.back_key
            )
            # os.remove(path)
        except Exception:
            await message.answer("Text is too long or wrong language")
    else:
        await message.answer("SEND YOUR TEXT❗:")
