from config import config, add_functionality
from dataclasses import dataclass, asdict

## TODO: Make state instance singleton

@dataclass
class State():
    current_index: int = 0
    current_size: int = 0
    index_count: int = 0
    
    def save(self: State) -> None:
        pass
    @classmethod
    def Factory[T: State](cls: type[T]) -> T:
        return cls()

# Add save method and Factory class method
add_functionality(State, config.__STATE_FILE__)

if __name__ == "__main__":
    data = State.Factory()
    print(data)