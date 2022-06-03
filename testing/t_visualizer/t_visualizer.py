from visualizer import Routines as VisRoutine
import pickle
from pathlib import Path

PICKLE_FILENAME = "test.pickle"


def load_pickle():
    p = Path(__file__).with_name(PICKLE_FILENAME)
    with open(p, "rb") as file:
        return pickle.load(file)


def test_visualizer():
    data = load_pickle()

    visualizer = VisRoutine(None)

    visualizer.run(_input=data["input"], output=data["output"], kwargs=data["kwargs"])


if __name__ == '__main__':
    test_visualizer()
