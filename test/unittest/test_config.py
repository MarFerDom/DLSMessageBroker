import pytest
from src.logger.config import config

def test_config_create():
    pass

def test_update():
    from json import load
    from os import remove
    _MEANING_OF_LIFE_ = 42
    config.__FILE_SIZE__ = _MEANING_OF_LIFE_
    config.save()

    try:
        with open(config._CONFIG_FULL_PATH_, 'r') as f:
            d = load(f)
        assert d["__FILE_SIZE__"] == _MEANING_OF_LIFE_, \
            f"File size is not {_MEANING_OF_LIFE_}"
        print(f"File was saved with edited value{(d["__FILE_SIZE__"] == _MEANING_OF_LIFE_)}")
    finally:
        remove(config._CONFIG_FULL_PATH_)