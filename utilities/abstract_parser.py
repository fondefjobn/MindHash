from abc import ABC, abstractmethod

"""
@Module: Parser
@Description: Abstract classes that define a parser
@Author: Lubor Budaj
"""

"""
Description: Abstract class for output of the parser
"""
class ParserOutput(ABC):

    """
    Description: Abstract function which should be overloaded, such that it output json
    """
    @abstractmethod
    def to_json(self):
        pass

"""
Description: Abstract class for input of the parser
"""
class ParserInput(ABC):

    """
    Description: Simple construtor calling initialize function
    """
    def __init__(self, data):
        self.initialize(data)

    """
    Description: Abstract function which should be overloaded to read the data
    """
    @abstractmethod
    def initialize(self, data):
        pass