import logging

from tools.pipes.p_template import State, RoutineSet


class Routines(RoutineSet):

    def LiveStream(self, state: State, *args):
        try:
            pass
        except Exception:
            logging.Logger.critical(msg='Failure to execute pipeline')
            exit(1)


class SensorController:
    """SensorController"""

    def __init__(self):
        pass

    def connect(self):
        pass
