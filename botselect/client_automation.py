import time

import keyboard
import pyautogui
import pyscreeze
import pywinauto
import win32gui

from botselect import config
from botselect import constants
from botselect import logger
from botselect import models

LOG = logger.getLogger(__name__)
APP = pywinauto.application.Application(backend="uia")

pyautogui.FAILSAFE = False


def automate_login(char_info: models.Character) -> bool:
    focus_game()
    state = constants.STATE_UNKNOWN
    progress_count = 0
    while state < constants.STATE_LOGIN and progress_count < 15:
        last_state = state
        try:
            state = progress_state()
        except LookupError:
            pass
        LOG.info(f"In state: {state}")
        progress_count += 1
        time.sleep(0.5)
        if state == last_state:
            move_mouse((0, 0))
            time.sleep(0.5)

    attempt_login(char_info)

    return True


def attempt_login(char_info: models.Character) -> bool:
    user_window = find_on_screen(config.IMG_LOGIN_USER_FIELD)
    if not user_window:
        return False
    click_mouse((
        user_window.left + int(user_window.width*7/8),  # Toward the right
        user_window.top + user_window.height + 8  # Just below
    ), 2)
    type_text('\b'*30)
    type_text(char_info.username)

    user_window = find_on_screen(config.IMG_LOGIN_PASSWORD_FIELD)
    if not user_window:
        return False
    click_mouse((
        user_window.left + int(user_window.width * 4 / 5),  # Toward the right
        user_window.top - 5  # Just above
    ))
    type_text('\b' * 30)
    type_text(char_info.password)
    time.sleep(0.5)

    if config.USE_QUICKCONNECT:
        user_window = find_on_screen(config.IMG_LOGIN_QUICKCONNECT)
        loc = (
            user_window.left + int(user_window.width/2),  # Middle
            user_window.top + 16  # Just below the top
        )
    else:
        loc = (
            user_window.left + int(user_window.width/2),  # Middle
            user_window.top + user_window.height - 14  # Just above the bottom
        )
    if not user_window:
        return False
    click_mouse(loc)
    return True


def progress_state() -> int:
    state = determine_state()
    if not state:
        LOG.error("Can't progress, state unknown.")
        raise LookupError("Can't determine state.")

    if state.state in (constants.STATE_EULA, constants.STATE_SPLASH,
                       constants.STATE_MAIN):
        click_mouse(get_center_of_box(state.area))

    return state.state


def get_center_of_box(box: pyscreeze.Box) -> pyscreeze.Point:
    return pyscreeze.Point(
        x=box.left + box.width/2,
        y=box.top + box.height/2
    )


def determine_state(
        last_state: int = constants.STATE_UNKNOWN) -> models.ScreenState:
    if last_state < constants.STATE_EULA:
        box = find_on_screen(config.IMG_EULA_BUTTON)
        if box:
            return models.ScreenState(state=constants.STATE_EULA, area=box)
    if last_state < constants.STATE_SPLASH:
        box = find_on_screen(config.IMG_SOE_LOGO)
        if box:
            return models.ScreenState(state=constants.STATE_SPLASH, area=box)
    if last_state < constants.STATE_MAIN:
        box = find_on_screen(config.IMG_LOGIN_BUTTON1)
        if not box:
            box = find_on_screen(config.IMG_LOGIN_BUTTON2)
        if box:
            return models.ScreenState(state=constants.STATE_MAIN, area=box)
    if last_state < constants.STATE_LOGIN:
        box = find_on_screen(config.IMG_LOGIN_USER_FIELD)
        if not box:
            box = find_on_screen(config.IMG_LOGIN_PASSWORD_FIELD)
        if not box:
            box = find_on_screen(config.IMG_LOGIN_QUICKCONNECT)
        if box:
            return models.ScreenState(state=constants.STATE_LOGIN, area=box)


def focus_game():
    # noinspection PyBroadException
    eqw = None
    try:
        if APP.process and APP.is_process_running():
            LOG.info("Already have APP handle.")
        else:
            if config.EQ_WINDOW_TITLE_REGEX:
                LOG.info("Connecting to APP via title regex.")
                APP.connect(title_re=config.EQ_WINDOW_TITLE_REGEX)
            else:
                LOG.info("Connecting to APP via window-class.")
                APP.connect(class_name="_EverQuestwndclass")

        if config.EQ_WINDOW_TITLE_REGEX:
            LOG.info("Getting window via title regex.")
            eqw = APP.window(title_re=config.EQ_WINDOW_TITLE_REGEX)
        else:
            LOG.info("Getting window via window-class.")
            eqw = APP.window(class_name="_EverQuestwndclass")

        LOG.info(f"Got window: {eqw}")
        # eqw.set_focus()
        LOG.info("Set focus.")
        win32gui.SetForegroundWindow(eqw.handle)
        LOG.info("Set foreground.")
        # keyboard.send('esc')  # why? no one knows, it's just required
    except pywinauto.findwindows.ElementNotFoundError:
        if eqw is None:
            LOG.error("EQ Window not found!")
    except pywinauto.findwindows.ElementAmbiguousError:
        LOG.error("Too many EQ Windows found?!")
    except Exception as e:
        LOG.error("Couldn't focus the game window!")
        print(e)


def find_on_screen(thing) -> pyscreeze.Box:
    # noinspection PyBroadException
    try:
        return pyautogui.locateOnScreen(thing, confidence=0.95)
    except Exception:
        LOG.error("Failed to capture screen. Try again next time?")


def find_center_on_screen(thing) -> pyscreeze.Point:
    # noinspection PyBroadException
    try:
        return pyautogui.locateCenterOnScreen(thing, confidence=0.875)
    except Exception:
        LOG.error("Failed to capture screen. Try again next time?")


def move_mouse(move_loc):
    pyautogui.moveTo(move_loc[0], move_loc[1])


def click_mouse(click_loc, times=1):
    move_mouse(click_loc)
    time.sleep(0.1)
    first = True
    for x in range(times):
        if not first:
            time.sleep(0.5)
        first = False
        pyautogui.mouseDown(click_loc[0], click_loc[1])
        time.sleep(0.2)
        pyautogui.mouseUp(click_loc[0], click_loc[1])


def type_text(the_text):
    # Ensure game window focus?
    # focus_game()
    for letter in the_text:
        if letter.isupper():
            keyboard.send("shift+" + letter)
        else:
            keyboard.write(letter, exact=False)
        time.sleep(0.02)
