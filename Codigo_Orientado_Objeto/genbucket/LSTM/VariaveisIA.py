from typing import Any

class VarIA:
    def __init__(self):
        self.name: str = None
        self.random_state = None
        self.test_size = None
        self.learning_rate = None
        self.epochs = None
        self.units = None

    def set(self, units, epochs, learning_rate, test_size, random_state):
        self.units: int = units
        self.epochs: int = epochs
        self.learning_rate: float = learning_rate
        self.test_size: float = test_size
        self.random_state: int = random_state
        self.name = f'{units}U_{epochs}E_{learning_rate}LR_{test_size}TS_{random_state}RS'

    def getName(self, num:int=1) -> str:
        return f'{self.name}_{num}NUMERO'

    def get(self) -> tuple[Any, Any, Any, Any, Any]:
        return self.units, self.epochs, self.learning_rate, self.test_size, self.random_state