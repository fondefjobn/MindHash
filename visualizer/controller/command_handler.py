import open3d as o3d


class CommandHandler:
    window: o3d.visualization.VisualizerWithKeyCallback
    commands = dict

    def __init__(self, model, window):
        self.model = model
        self.window = window

        self.setup_command_map()
        self.register_commands()

    def setup_command_map(self):
        commands = dict()
        commands[32] = self.toggle_pause  # space bar
        commands[256] = self.quit  # escape

        self.window.register_key_callback(32, self.toggle_pause)

        self.commands = commands

    def register_commands(self):
        for key in self.commands:
            self.window.register_key_callback(key, self.commands[key])

    def toggle_pause(self, vis):
        self.model.paused = not self.model.paused
        return False

    def quit(self, vis):
        self.model.stop()
