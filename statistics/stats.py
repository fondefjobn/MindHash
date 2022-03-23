from tools.pipes.p_tmpl import Pipeline, State


class Statistics(Pipeline):

    def execute(self, prev):
        super().execute(prev)
        # code goes here
        super().update(prev)
