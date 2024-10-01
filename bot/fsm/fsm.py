from aiogram.fsm.state import StatesGroup, State


class MiniDialogSG(StatesGroup):
    greeting = State()
    name = State()
    hearth_button = State()
    end = State()
    story_crystal = State()
    what_is_crystal = State()
    what_types_of_layouts = State()
    types_info = State()
    energy = State()


class CardPerDaySG(StatesGroup):
    in_process = State()
    ending = State()
    thankful = State()


class CardThreeSG(StatesGroup):
    in_process = State()
    ending = State()
    thankful = State()


class CardFiveSG(StatesGroup):
    in_process = State()
    ending = State()
    thankful = State()


class CardQuestionSG(StatesGroup):
    waiting_for_question = State()
    ask_question = State()
    in_process = State()
    ending = State()
    thankful = State()


class GratitudeSG(StatesGroup):
    gratitude = State()


class AdminSG(StatesGroup):
    in_adm = State()


class AdminUsersSG(StatesGroup):
    check_users = State()


class AdminStatisticsSG(StatesGroup):
    stats = State()


class AdminAdvSG(StatesGroup):
    adv = State()
    adv_pictures = State()
    adv_url = State()
    adv_url_btn_name = State()
    adv_text = State()

    adv_change_text = State()
    adv_change_pics = State()
    adv_change_url = State()
    adv_change_url_btn_name = State()


class AdminNotifyUsersSG(StatesGroup):
    notify_date = State()
    notify_text = State()
