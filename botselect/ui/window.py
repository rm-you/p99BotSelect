import ObjectListView
import wx

from botselect import client_automation
from botselect import config
from botselect import logger
from botselect import overrides
from botselect import utils
from botselect.ui import events

# This is the app logger, not related to EQ logs
LOG = logger.getLogger(__name__)
# Monkeypatch ObjectListView to fix a character encoding bug (PR upstream?)
# pylint: disable=protected-access
ObjectListView.ObjectListView._HandleTypingEvent = overrides.HandleTypingEvent
ObjectListView.ObjectListView._HandleSize = overrides.HandleSize


class MainWindow(wx.Frame):
    def __init__(self, parent=None, title="Bot Selector"):
        wx.Frame.__init__(self, parent, title=title, size=(560, 600))
        icon = wx.Icon()
        # icon.CopyFromBitmap(
        #     wx.Bitmap(os.path.join(
        #         config.PROJECT_DIR, "data", "icons", "ninja_attack.png"),
        #               wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(events.EVT_REFRESH_PROGRESS, self.refresh_progress)
        self.Bind(events.EVT_REFRESH_COMPLETE, self.refresh_complete)

        # Set up taskbar icon
        # config.WX_TASKBAR_ICON = TaskBarIcon(self)

        characters_box = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(characters_box)

        buttons_box = wx.BoxSizer(wx.HORIZONTAL)
        button_refresh = wx.Button(self, label="Refresh List")
        button_refresh.Bind(wx.EVT_BUTTON, self.refresh)
        self.button_refresh = button_refresh
        button_login = wx.Button(self, label="Login")
        button_login.Bind(wx.EVT_BUTTON, self.login)
        button_login.Disable()
        self.button_login = button_login
        buttons_box.Add(button_refresh, flag=wx.LEFT | wx.RIGHT, border=120)
        buttons_box.Add(button_login)
        characters_box.Add(buttons_box, flag=wx.EXPAND | wx.ALL, border=5)

        characters_list = ObjectListView.ObjectListView(
            self, wx.ID_ANY, style=wx.LC_REPORT | wx.LC_SINGLE_SEL,
            size=wx.Size(500, 600))
        characters_box.Add(characters_list, flag=wx.EXPAND | wx.ALL)
        self.characters_list = characters_list

        characters_list.SetColumns([
            ObjectListView.ColumnDefn(
                "Name", "left", 140, "name",
                fixedWidth=140),
            ObjectListView.ColumnDefn(
                "Username", "left", 120, "username",
                fixedWidth=120),
            ObjectListView.ColumnDefn(
                "Password", "left", 120, "password",
                fixedWidth=120),
            ObjectListView.ColumnDefn(
                "Class", "left", 90, "_class",
                fixedWidth=90),
            ObjectListView.ColumnDefn(
                "Level", "left", 50, "level",
                fixedWidth=50),
        ])
        characters_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.selected_char)
        characters_list.SetEmptyListMsg("No characters loaded.")
        try:
            data = utils.load_cache()
            characters_list.SetObjects(data)
        except Exception as e:
            LOG.warning(f"Couldn't load cache file: {e}")
            characters_list.SetObjects([])

        self.Show(True)

    def refresh(self, e: wx.Event):
        self.button_refresh.Disable()
        self.button_login.Disable()
        self.characters_list.SetEmptyListMsg("Refreshing list: 0%")
        self.characters_list.SetObjects([])

        config.EXECUTOR.submit(self.refresh_async)

    def refresh_async(self):
        data = utils.fetch_google_sheet_data(self)
        print(len(data))
        event = events.RefreshCompleteEvent(data=data)
        wx.PostEvent(self, event)

    def refresh_progress(self, e: wx.Event):
        percent = int(e.percent)
        LOG.info(f"Refresh progress: {percent}%")
        self.characters_list.SetEmptyListMsg(f"Refreshing list: {percent}%")

    def refresh_complete(self, e: wx.Event):
        data = e.data
        self.characters_list.SetObjects(data)
        utils.store_cache(data)
        self.characters_list.SetEmptyListMsg("No characters loaded.")
        self.button_refresh.Enable()

    def selected_char(self, e: wx.Event):
        self.button_login.Enable()

    def login(self, e: wx.Event):
        character = self.characters_list.GetSelectedObject()
        LOG.info(f"Logging in {character.name}")
        client_automation.automate_login(character)

    def on_close(self, e: wx.Event):
        self.Destroy()
