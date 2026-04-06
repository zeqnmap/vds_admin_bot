from aiogram.fsm.state import State, StatesGroup


class WeldingFSM(StatesGroup):
    fullname = State()
    project = State()
    efficiency = State()
    red_reason = State()
    problem_type = State()
    problem_desc = State()
    question_desc = State()
    photo_optional = State()


class AuxiliaryFSM(StatesGroup):
    fullname = State()
    project = State()
    efficiency = State()
    red_reason = State()
    problem_type = State()
    problem_desc = State()
    question_desc = State()
    photo_optional = State()


class PreparatoryFSM(StatesGroup):
    fullname = State()
    project = State()
    efficiency = State()
    red_reason = State()
    problem_type = State()
    problem_desc = State()
    question_desc = State()
    photo_optional = State()


class AssemblyFSM(StatesGroup):
    fullname = State()
    project = State()
    efficiency = State()
    red_reason = State()
    problem_type = State()
    problem_desc = State()
    question_desc = State()
    photo_optional = State()


class RviFSM(StatesGroup):
    fullname = State()
    project = State()
    efficiency = State()
    red_reason = State()
    problem_type = State()
    problem_desc = State()
    question_desc = State()
    photo_optional = State()


# ====================== АДМИН ======================


class AdminFSM(StatesGroup):
    waiting_for_workshop_add = State()
    waiting_for_project_name = State()
    waiting_for_workshop_remove = State()
    waiting_for_project_remove = State()


# ====================== КРЕАТИВ ======================


class CreativeFSM(StatesGroup):
    fullname = State()
    project = State()
    efficiency = State()
    red_reason = State()
    problem_type = State()
    problem_desc = State()
    question_desc = State()
    photo_optional = State()


# ====================== ПРОДАЖИ ======================


class SalesFSM(StatesGroup):
    fullname = State()
    project = State()
    efficiency = State()
    red_reason = State()
    problem_type = State()
    problem_desc = State()
    question_desc = State()
    photo_optional = State()


# ====================== КБ ======================


class KbFSM(StatesGroup):
    fullname = State()
    project = State()
    efficiency = State()
    red_reason = State()
    problem_type = State()
    problem_desc = State()
    question_desc = State()
    photo_optional = State()


# ====================== ЛОГИСТИКА ======================


class LogisticsFSM(StatesGroup):
    fullname = State()
    project = State()
    efficiency = State()
    red_reason = State()
    problem_type = State()
    problem_desc = State()
    question_desc = State()
    photo_optional = State()


# ====================== МОНТАЖ ======================


class InstallationFSM(StatesGroup):
    fullname = State()
    project = State()
    efficiency = State()
    red_reason = State()
    problem_type = State()
    problem_desc = State()
    question_desc = State()
    photo_optional = State()

# ======================  ======================

class PassportFSM(StatesGroup):
    fullname = State()
    project = State()
    efficiency = State()
    red_reason = State()
    problem_type = State()
    problem_desc = State()
    question_desc = State()
    photo_optional = State()

# ======================  ======================

class SupplyFSM(StatesGroup):
    fullname = State()
    project = State()
    efficiency = State()
    red_reason = State()
    problem_type = State()
    problem_desc = State()
    question_desc = State()
    photo_optional = State()

# ======================  ======================

class EconomicsFSM(StatesGroup):
    fullname = State()
    project = State()
    efficiency = State()
    red_reason = State()
    problem_type = State()
    problem_desc = State()
    question_desc = State()
    photo_optional = State()