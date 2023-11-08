import concurrent.futures
import datetime
import json
import urllib.parse

import requests
import wx

from botselect import config
from botselect import constants
from botselect import logger
from botselect import models
from botselect.ui import events

# This is the app logger, not related to EQ logs
LOG = logger.getLogger(__name__)


def fetch_google_sheet_data(ui_frame: wx.Frame) -> list[models.Character]:
    data = []

    # Get the data in JSON format
    new_url = constants.BASE_SHEET_URL.format(id=config.SHEET_ID)
    req = requests.get(new_url, params={'alt': 'json', 'key': config.API_KEY})
    if req.status_code != 200:
        LOG.error("Couldn't fetch primary spreadsheet `%s`: %d",
                  config.SHEET_ID, req.status_code)
        return data

    sheets = req.json()['sheets']
    sheet_list: list[str] = [sheet['properties']['title'] for sheet in sheets]
    event = events.RefreshProgressEvent(
        percent=1 / (len(sheet_list) + 1) * 100)
    wx.PostEvent(ui_frame, event)

    futures = {config.EXECUTOR.submit(parse_sheet_page, _class): _class
               for _class in sheet_list}

    count = 1
    LOG.info(f"Waiting for {len(futures)} futures...")
    for future in concurrent.futures.as_completed(futures):
        LOG.info(f"Completed future: {futures[future]}")
        count += 1
        event = events.RefreshProgressEvent(percent=count/(len(futures)+1)*100)
        wx.PostEvent(ui_frame, event)
        data.extend(future.result())
    LOG.info("All futures complete.")
    return data


def parse_sheet_page(_class: str) -> list[models.Character]:
    data = []
    class_name = convert_class_name(_class)
    class_sheet_url = constants.CLASS_SHEET_URL.format(
        id=config.SHEET_ID, key=config.API_KEY,
        _class=urllib.parse.quote_plus(_class))
    class_sheet_req = requests.get(
        class_sheet_url,
        params={'alt': 'json', 'key': config.API_KEY})
    if class_sheet_req.status_code != 200:
        LOG.error("Couldn't fetch secondary spreadsheet `%s`: %d",
                  _class, class_sheet_req.status_code)
        return data

    class_sheet_data: list = class_sheet_req.json()['values']

    for index, row in enumerate(class_sheet_data):
        if 'username' in map(str.lower, row):
            header_row = index
            LOG.info(f"{_class}: Header row = {header_row}")
            break
    else:
        LOG.warning(f"No username column found for: {_class}")
        return data

    header: list[str] = class_sheet_data[header_row]
    try:
        name_column = find_column_index('name', header)
        user_column = find_column_index('username', header)
        pass_column = find_column_index('password', header)
    except ValueError:
        LOG.warning(f"Missing required columns in sheet: {_class}")
        return data

    for row in class_sheet_data[header_row+1:]:
        if len(row) < 3:
            break
        char_obj = models.Character(
            name=row[name_column],
            _class=class_name,
            username=row[user_column],
            password=row[pass_column]
        )
        try:
            level_column = find_column_index('lvl', header)
            lvl = row[level_column]
            if ':' in lvl:
                lvl: str = lvl.split(':')[-1].strip("% ")
                lvl = lvl.replace(' ', '.')
            elif ' ' in lvl:
                lvl = lvl.split(' ')[-1].strip("% ")
            char_obj.level = lvl
        except ValueError:
            pass
        if char_obj.name:
            data.append(char_obj)

    return data


def find_column_index(column_name: str, row: list[str]) -> int:
    return tuple(map(str.lower, row)).index(column_name.lower())


def convert_class_name(name: str) -> str:
    for class_name in constants.ALL_CLASSES:
        if class_name.lower().startswith(name[:3].lower()):
            return class_name
    LOG.warning(f"Failed to convert class name: {name}")
    return name


def load_cache() -> list[models.Character]:
    with open(config.CACHE_FILE, 'r') as cache_file:
        data = json.load(cache_file, cls=JSONDecoder)
    return data


def store_cache(data: list[models.Character]) -> None:
    with open(config.CACHE_FILE, 'w') as cache_file:
        json.dump(data, cache_file, cls=JSONEncoder)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):  # pylint: disable=arguments-differ
        try:
            return o.to_json()
        except AttributeError:
            if isinstance(o, datetime.datetime):
                return o.isoformat()
            return json.JSONEncoder.default(self, o)


# Mutated from https://github.com/AlexisGomes/JsonEncoder/
class JSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):  # pylint: disable=method-hidden
        if isinstance(obj, dict):
            if 'json_type' in obj:
                json_type = obj.pop('json_type')
                model_type = getattr(models, json_type)
                if model_type and issubclass(model_type, models.DictEquals):
                    try:
                        return model_type.from_json(**obj)
                    except Exception:
                        LOG.error(f"Failed to parse json object: {obj}")

        # handling the resolution of nested objects
        if isinstance(obj, dict):
            for key in list(obj):
                obj[key] = self.object_hook(obj[key])

        return obj
