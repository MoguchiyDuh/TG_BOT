from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class LANG_Callback(CallbackData, prefix="lang"):
    lang: str


class SPEAKER_Callback(CallbackData, prefix="speaker"):
    speaker: str


def create_inline_lang_keyboard(languages) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    [
        builder.button(text=language, callback_data=f"lang:{language}")
        for language in languages
    ]
    builder.adjust(*([3] * (len(languages) // 3)))
    return builder.as_markup()


def create_inline_speakers_keyboard(
    speakers: list,
) -> InlineKeyboardMarkup | list[InlineKeyboardMarkup]:
    builder = InlineKeyboardBuilder()
    if len(speakers) > 100:
        builders = []
        for i in range(0, len(speakers), 100):
            subarray = speakers[i : i + 100]
            [
                builder.button(text=speaker, callback_data=f"speaker:{speaker}")
                for speaker in subarray
            ]
            builder.adjust(*([5] * (len(subarray) // 5)))
            builders.append(builder.as_markup())
            builder = InlineKeyboardBuilder()
        return builders
    else:
        [
            builder.button(text=speaker, callback_data=f"speaker:{speaker}")
            for speaker in speakers
        ]
        builder.adjust(*([5] * (len(speakers) // 5)))
        return builder.as_markup()


def create_reply_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    keyboard_list = (
        "/text_from_image🖼",
        "/speech_to_text🎤",
        "/text_to_speech💬",
        "/status❓",
    )
    [builder.button(text=key) for key in keyboard_list]
    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()


back_key = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/back🔙")]])
