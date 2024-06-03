from aiogram.fsm.state import State, StatesGroup


class FSM(StatesGroup):
    sending_image = State()
    sending_audio = State()
    sending_text = State()
