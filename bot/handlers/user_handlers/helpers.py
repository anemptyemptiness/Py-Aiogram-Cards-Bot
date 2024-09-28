from aiogram.fsm.context import FSMContext


async def is_user_in_payment(state: FSMContext):
    current_state = await state.get_state()

    if current_state:
        try:
            if current_state.split(":")[1] == "thankful":
                return True
        except Exception:
            return False
    return False
