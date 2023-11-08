from __future__ import annotations

import pyscreeze

from botselect import constants


class DictEquals:
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        self_dict = {key: self.__dict__[key] for key in self.__dict__
                     if not key.startswith("__")}
        other_dict = {key: other.__dict__[key] for key in other.__dict__
                      if not key.startswith("__")}
        return self_dict == other_dict

    def to_json(self):
        json_dict = {key: self.__dict__[key] for key in self.__dict__
                     if not key.startswith("__")}
        return {
            'json_type': self.__class__.__name__,
            **json_dict
        }

    @classmethod
    def from_json(cls, **kwargs) -> DictEquals:
        return cls(**kwargs)


class Character(DictEquals):
    name: str = None
    _class: str = None
    level: str = None
    username: str = None
    password: str = None

    def __init__(self, name: str, _class: str, username: str, password: str,
                 level: str = ""):
        self.name = name
        self._class = _class
        self.level = level
        self.username = username
        self.password = password


class ScreenState:
    state: int = constants.STATE_UNKNOWN
    area: pyscreeze.Box = None

    def __init__(self, state: int, area: pyscreeze.Box):
        self.state = state
        self.area = area
