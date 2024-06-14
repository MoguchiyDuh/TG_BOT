from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
import os
from diffusers import AutoPipelineForText2Image
import torch
from dotenv import load_dotenv
from time import localtime, strftime
from fsm import FSM
import keyboard

load_dotenv()
router = Router()

CALLBACK_DATA = ""
IMAGES_DIR = "picture_gen/pictures"
CONFIG = {
    "prompt": "",
    "negative_prompt": "",
    "model": os.getenv("STABLE_DIFFUSION_MODEL"),
    "steps": 20,
    "height": 512,
    "width": 512,
    "seed": -1,
}


def return_config_text(config: dict) -> str:
    text = ""
    for key, value in config.items():
        text += f"{key}: {value}\n"
    return text


def is_integer(s: str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


def generate_image():
    global CONFIG
    generator = torch.Generator("cuda")
    generator.manual_seed(CONFIG["seed"])
    CONFIG["seed"] = generator.seed()
    pipe = AutoPipelineForText2Image.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.bfloat16,
        use_safetensors=True,
    )
    pipe.enable_model_cpu_offload()
    image = pipe(
        prompt=CONFIG["prompt"],
        negative_prompt=CONFIG["negative_prompt"],
        num_inference_steps=CONFIG["steps"],
        height=CONFIG["height"],
        width=CONFIG["width"],
        generator=generator,
    ).images[0]
    return image


@router.message(Command("image_generation🖼"))
async def set_state_sending_image(message: Message, state: FSMContext):
    await state.set_state(FSM.sending_prompt)
    await message.answer("Write your prompt:", reply_markup=keyboard.back_key)
    # await message.answer(
    #     return_config_text(CONFIG),
    #     reply_markup=keyboard.create_inline_gen_keyboard(CONFIG.keys()),
    # )


@router.message(FSM.sending_prompt)
async def set_prompt(message: Message, state: FSMContext):
    global CONFIG
    if message.text != None:
        CONFIG["prompt"] = message.text
        await state.clear()
        await message.answer(
            return_config_text(CONFIG),
            reply_markup=keyboard.create_inline_gen_keyboard(CONFIG.keys()),
        )
    else:
        await message.answer("SEND YOUR TEXT❗:")


@router.callback_query(keyboard.GEN_Callback.filter(F.key == "generate"))
async def generate(query: CallbackQuery):
    global CONFIG
    await query.message.answer("Generating⚙")
    timecode = strftime("%Y.%m.%d-%H.%M.%S", localtime())
    if not os.path.isdir(f"{IMAGES_DIR}/{query.from_user.id}"):
        os.mkdir(f"{IMAGES_DIR}/{query.from_user.id}")
    image_path = f"{IMAGES_DIR}/{query.from_user.id}/{timecode}.png"
    generate_image().save(image_path)
    await query.message.answer_photo(photo=FSInputFile(image_path))
    await query.message.answer(text=f"seed: {CONFIG["seed"]}")


@router.callback_query(keyboard.GEN_Callback.filter(F.key != "generate"))
async def lang_handler(
    query: CallbackQuery,
    callback_data: keyboard.GEN_Callback,
    state: FSMContext,
):
    global CALLBACK_DATA
    await query.message.answer(f"Enter your {callback_data.key}:")
    await state.set_state(FSM.sending_gen_setting)
    CALLBACK_DATA = callback_data.key


@router.message(FSM.sending_gen_setting)
async def set_seed(message: Message, state: FSMContext):
    global CONFIG, CALLBACK_DATA
    if message.text != None:
        if CALLBACK_DATA in list(CONFIG.keys())[:2]:
            CONFIG[CALLBACK_DATA] = message.text
        elif CALLBACK_DATA == list(CONFIG.keys())[2]:
            pass
        elif CALLBACK_DATA in list(CONFIG.keys())[3:]:
            try:
                CONFIG[CALLBACK_DATA] = int(message.text)
            except ValueError:
                await message.answer("THE KEY MUST BE AN INT❗:")
                return 0

        await message.answer(
            return_config_text(CONFIG),
            reply_markup=keyboard.create_inline_gen_keyboard(CONFIG.keys()),
        )
        await state.clear()
    else:
        await message.answer("SEND YOUR TEXT❗:")
