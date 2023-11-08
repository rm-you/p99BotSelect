# Player Classes
BARD = "Bard"
CLERIC = "Cleric"
DRUID = "Druid"
ENCHANTER = "Enchanter"
MAGICIAN = "Magician"
MONK = "Monk"
NECROMANCER = "Necromancer"
PALADIN = "Paladin"
RANGER = "Ranger"
ROGUE = "Rogue"
SHADOW_KNIGHT = "SK"
SHAMAN = "Shaman"
WARRIOR = "Warrior"
WIZARD = "Wizard"

# Raid Roles
TANKS = (WARRIOR, PALADIN, SHADOW_KNIGHT)
KNIGHTS = (PALADIN, SHADOW_KNIGHT)
PRIESTS = (CLERIC, DRUID, SHAMAN)
MELEE = (BARD, MONK, RANGER, ROGUE)
CASTERS = (ENCHANTER, MAGICIAN, NECROMANCER, WIZARD)

ALL_CLASSES = set(TANKS + PRIESTS + MELEE + CASTERS)

BASE_SHEET_URL = "https://sheets.googleapis.com/v4/spreadsheets/{id}"
CLASS_SHEET_URL = (
    "https://sheets.googleapis.com/v4/spreadsheets/{id}/values/{_class}")

STATE_UNKNOWN = 0
STATE_EULA = 1
STATE_SPLASH = 2
STATE_MAIN = 3
STATE_LOGIN = 4
