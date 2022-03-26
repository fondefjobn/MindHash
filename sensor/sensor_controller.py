import logging

from tools.pipes.p_tmpl import Pipeline, State


class LiveStream(Pipeline):

    def run(self):
        super().run()
        try:
            pass
        except Exception:
            logging.Logger.critical('Failure to execute pipeline')
            exit(1)


class SensorController:
    """SensorController"""

    def __init__(self):
        pass

    def connect(self):
        pass
