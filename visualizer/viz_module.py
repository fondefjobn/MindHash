from tools.pipes.p_tmpl import Pipeline,State


class Visualization(Pipeline):

    def execute(self, prev) :
        super().execute(prev)
        super().update(prev)


class Visualizer:

    def __init__(self):
        pass
