import open3d as o3d

"""
@Module: Command Handler
@Description: The control module that contains all the commands for the visualizer.
It gets all commands, and passes them to the open3d Visualizer so that they
are called when the corresponding keys are pressed.
@Author: Bob van der Vuurst
"""


class CommandHandler:
    window: o3d.visualization.VisualizerWithKeyCallback
    commands: dict

    def __init__(self, model, window):
        self.model = model
        self.window = window

        self.setup_command_map()
        self.register_commands()

    """
    Add all commmands to the command maps with their corresponding keys.
    The key codes are defined by the c++ GLFW library used by the open3d visualizer.
    Those definitions can be found here: https://www.glfw.org/docs/latest/group__keys.html
    """
    def setup_command_map(self):
        self.commands = dict()
        self.commands[32] = self.toggle_pause  # space bar
        self.commands[256] = self.quit  # escape
        self.commands[263] = self.previous_frame  # left
        self.commands[262] = self.next_frame  # right
        self.register_commands()

    """
    Take all the commands and their keys from the command map, then register them at the open3d visualizer.
    """
    def register_commands(self):
        for key in self.commands:
            self.window.register_key_callback(key, self.commands[key])

    """
    A command to toggle if the model is paused or not. 
    """
    def toggle_pause(self, vis):
        self.model.paused = not self.model.paused
        return False

    """
    A command to move one step back to the previous frame. 
    The model is paused so that it does not immediately move back to the current frame.
    The command returns True to indicate that the view needs to be updated.
    """
    def previous_frame(self, vis):
        self.model.paused = True
        if self.model.frame > 0:
            self.model.frame -= 1
        return True

    """
    A command to move one step forward to the next frame. 
    The model is paused so that it does not immediately go to the next frames.
    The command returns True to indicate that the view needs to be updated.
    """
    def next_frame(self, vis):
        self.model.paused = True
        if self.model.frame + 1 < len(self.model.points):
            self.model.frame += 1
        return True

    """
    A command to stop the model and the view.
    """
    def quit(self, vis):
        self.model.stop()
        return True
