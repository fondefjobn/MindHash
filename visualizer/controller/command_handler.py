import open3d as o3d


class CommandHandler:
    window: o3d.visualization.VisualizerWithKeyCallback
    commands: dict

    def __init__(self, model, window):
        self.model = model
        self.window = window

        self.setup_command_map()
        self.register_commands()

    def setup_command_map(self):
        self.commands = dict()
        self.commands[32] = self.toggle_pause  # space bar
        self.commands[256] = self.quit  # escape
        self.commands[263] = self.previous_frame  # left
        self.commands[262] = self.next_frame  # right

        self.register_commands()

    def register_commands(self):
        for key in self.commands:
            self.window.register_key_callback(key, self.commands[key])

    def toggle_pause(self, vis):
        self.model.paused = not self.model.paused
        return False

    def previous_frame(self, vis):
        self.model.paused = True
        if self.model.frame > 0:
            self.model.frame -= 1
        return True

    def next_frame(self, vis):
        self.model.paused = True
        if self.model.frame + 1 < len(self.model.points):
            self.model.frame += 1
        return True

    def quit(self, vis):
        self.model.stop()
