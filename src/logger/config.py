import os
from typing import ClassVar, Callable, Any
from dataclasses import dataclass, asdict
from json import dump, load

@dataclass
class Config():
    '''
        Configuration file interface

        Since uses Factory, singleton doesn't need to be implemented in __new__
    '''
    # Path to config file
    _CONFIG_PATH_: ClassVar[str] = os.getenv("DSLMB_CONFIG_FILE") or "."
    _CONFIG_FILE_NAME_: ClassVar[str] = ".file_handler.conf"
    _CONFIG_FULL_PATH_: ClassVar[str] = \
        os.path.join(_CONFIG_PATH_, _CONFIG_FILE_NAME_)
    __LOG_FOLDER__: str = os.path.join(".",".LOGS")
    __INDEX_FILE__: str = ".index"
    __LOG_FILE__: str = ".log"
    __FILE_SIZE__: int = 1<<32
    __STATE_FILE__: str = ".state"

    # Keep track of singleton instance
    instance: ClassVar[Config | None] = None

    # Dummy save and Factory to avoid fighting lint
    def save(self: Config) -> None:
        pass
    @classmethod
    def Factory[T: Config](cls: type[T]) -> T:
        return cls()

def add_functionality(cls: Any, filepath: str) -> None:
    '''
        Add save method and factory class method to cls
    '''
    # __str__ goes through dict first
    cls.__str__ = lambda self: str(asdict(self))

    # Add as InstanceMethod with given filepath to make save method
    def save_dataclass(filepath:str) -> Callable[...,None]:
        def save(self) -> None:
            '''
                Save contents of dataclass in file as dictionary
            '''
            with open(filepath, 'w') as f:
                dump(str(self), f)
        return save

    # Add save method to class Config
    setattr(cls, "save", save_dataclass(filepath))

    # Add as ClassMethod with given filepath to make factory
    def blueprint(filepath: str) -> Callable[...,Any]:
        def factory(cls):
            '''
                Creates new object from class from saved file
                if it exists, or default values otherwise
            '''
            if cls.instance is not None: return cls.instance
            d = {}
            # Read from file if it exists
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    d = load(f)
            cls.instance = cls(**d)
            return cls.instance
        return factory

    # Add factory method to class Config
    setattr(cls, "Factory", classmethod(blueprint(filepath)))

    # __del__ guarantees saving before closing
    def delete(self):
        if hasattr(self, 'save'):
            getattr(self, 'save')()
        super(self).__del__()
    cls.__del__ = delete

add_functionality(Config, Config._CONFIG_FULL_PATH_)

config = Config.Factory()
config.save()