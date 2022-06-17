import pickle
import unittest
from abc import ABC
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Tuple

from tools.pipeline import RNode, Pipeline, State
from tools.pipeline.routines import RoutineSet
from tools.structs import PopList

OUTPUT: str = "output"


class Rs(RoutineSet):

    def __all__(self) -> set:
        return {Add, Sub, Read, Mod, Div}

    def activationList(self, a: Namespace) -> List[Tuple[object, RNode]]:
        return [(True, Add),
                (True, Sub),
                (True, Read),
                (True, Mod),
                (True, Div), ]


class Arithmetic(RNode, ABC):
    idx: int = 0

    def get_index(self) -> int:
        return self.idx

    @classmethod
    def script(cls, parser: ArgumentParser) -> bool:
        return True

    def fconfig(self) -> str:
        return None


class Read(Arithmetic):
    def __init__(self, state):
        super().__init__(state)

    @RNode.assist
    def run(self, _input: List[PopList], output: PopList, **kwargs):
        for i in list(range(0, 10)):
            output.append(i)

    def dependencies(self) -> list:
        return []


class Add(Arithmetic):
    def __init__(self, state):
        super().__init__(state)

    @RNode.assist
    def run(self, _input: List[PopList], output: PopList, **kwargs):
        while not _input[0].full(self.idx):
            var0: float = _input[0].qy(self.idx, self.event)
            output.append(var0 + var0 + 55)
            self.idx += 1

    def dependencies(self) -> list:
        return [Read]


class Mod(Arithmetic):
    def __init__(self, state):
        super().__init__(state)

    @RNode.assist
    def run(self, _input: List[PopList], output: PopList, **kwargs):
        while not _input[0].full(self.idx):
            output.append(_input[0].qy(self.idx, self.event) % 17)
            self.idx += 1

    def dependencies(self) -> list:
        return [Add]


class Sub(Arithmetic):
    def __init__(self, state):
        super().__init__(state)

    @RNode.assist
    def run(self, _input: List[PopList], output: PopList, **kwargs):
        while not _input[0].full(self.idx):
            var0: int = _input[0].qy(self.idx, self.event)
            var1: int = _input[1].qy(self.idx, self.event)
            output.append(var0 - var1)
            self.idx += 1

    def dependencies(self) -> list:
        return [Mod, Read]


class Div(Arithmetic):
    def __init__(self, state):
        super().__init__(state)

    @RNode.assist
    def run(self, _input: List[PopList], output: PopList, **kwargs):
        while not _input[0].full(self.idx):
            output.append(_input[0].qy(self.idx, self.event) / 10)
            self.idx += 1
        self.state[OUTPUT] = [_ for _ in output.values()]

    def dependencies(self) -> list:
        return [Sub]


class PipelineBuildTest(unittest.TestCase):
    correct_output = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, -0.6, -0.5, -0.4]

    def test_pipeline(self):
        pd = Pipeline()
        state: State = pd.build_pipeline(state=State(parser=None), rs=Rs())
        pd.execute_pipeline()
        self.assertEqual(state["output"], self.correct_output)


if __name__ == '__main__':
    unittest.main()
