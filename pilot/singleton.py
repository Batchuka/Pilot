from abc import ABC, abstractmethod

class Singleton(ABC):
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls] = instance
            instance._initialize(*args, **kwargs)  # Chama o método _initialize após a criação da instância
        return cls._instances[cls]

    @abstractmethod
    def _initialize(self, *args, **kwargs):
        """Método abstrato que deve ser implementado em todas as subclasses."""
        pass