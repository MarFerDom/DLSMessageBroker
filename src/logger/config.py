import os
from typing import ClassVar
from dataclasses import dataclass, asdict
from json import dump, load

@dataclass
class Config():

    # Path to config file
    _CONFIG_PATH_: ClassVar = os.getenv("DSLMB_CONFIG_FILE") or "."
    _CONFIG_FILE_NAME_: ClassVar = ".file_handler.conf"
    _CONFIG_FULL_PATH_: ClassVar = os.path.join(_CONFIG_PATH_, _CONFIG_FILE_NAME_)

    __LOG_FOLDER__: str = os.path.join(".",".LOGS")
    __INDEX_FILE__: str = ".index"
    __LOG_FILE__: str = ".log"
    __FILE_SIZE__: int = 1<<32
    __STATE_FILE__: str = ".state"

    def save(self):
        with open(Config._CONFIG_FULL_PATH_, 'w') as f:
            dump(asdict(self), f)

d = {}
# Read from file if exists
if os.path.exists(Config._CONFIG_FULL_PATH_):
    with open(Config._CONFIG_FULL_PATH_, 'w') as f:
        d = load(f)

config = Config(**d)
config.save()