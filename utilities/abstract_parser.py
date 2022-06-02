from abc import ABC, abstractmethod

class ParserOutput(ABC):

    @abstractmethod
    def to_json(self):
        pass

class ParserInput(ABC):

    def __init__(self, data):
        self.initialize(data)

    @abstractmethod
    def initialize(self, data):
        pass