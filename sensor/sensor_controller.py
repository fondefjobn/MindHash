import logging

from tools.pipes import State, RoutineSet
from tools.structs.custom_structs import PopList
from utilities.utils import IO


class Routines(RoutineSet):

    def id(self):
        return "SENSOR_BUNDLE"

    def LiveStream(self, state: State, *args):
        try:
            pass
        except Exception:
            logging.Logger.critical(msg='Failure to execute pipeline')
            exit(1)

    def UserInput(self, state: State, *args):
        """
        Routine: User Input File post-process

        Produces: UserInput
        Consumes: User provided input
        Requires: Pcap path
        Parameters
        ----------
        state
        args (input_list, output_list)

        Returns
        -------

        """
        with open(state.args.meta, 'r') as f:
            out_ls: PopList = args[1]
            getattr(IO, state.args.sensor)(state.args, f, out_ls)
            out_ls.set_full()
        Routines.logging.info(msg='UserInput reading: done')


class SensorController:
    """SensorController"""

    def __init__(self):
        pass

    def connect(self):
        pass
