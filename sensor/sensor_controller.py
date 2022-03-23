import logging

from tools.pipes.p_tmpl import Pipeline, State


class LiveStream(Pipeline):

    def execute(self, prev):
        super().execute(prev)
        try:
            pass
        except Exception:
            logging.Logger.critical('Failure to execute pipeline')
            exit(1)
        super().update(prev)


class SensorController:
    """SensorController"""

    def __init__(self):
        pass

    def connect(self):
        pass
