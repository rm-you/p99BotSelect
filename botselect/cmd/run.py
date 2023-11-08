import sys
import traceback

import wx

from botselect import logger
from botselect.ui import window

LOG = logger.getLogger(__name__)


def run():
    app = wx.App(False)
    if getattr(sys, 'frozen', False):
        try:
            # autoupdate.check_update()
            pass
        except SystemExit:
            return
        except:  # noqa
            LOG.exception(
                "Failed to automatically update. Continuing with old version.")

    # extra_data.apply_sheet_overrides()
    # extra_data.apply_custom_overrides()
    # utils.load_state()
    window.MainWindow()
    app.MainLoop()


if __name__ == "__main__":
    try:
        run()
    except:  # noqa
        with open("bs-crash-log.txt", "w") as f:
            traceback.print_exc(file=f)
        raise
