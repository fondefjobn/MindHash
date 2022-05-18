import open3d as o3d
import open3d.visualization.gui as gui


class Window:

    def __init__(self):
        interface = gui.Application.instance.create_window("Mindhash", 1920, 1080)

        frame = gui.Horiz()

        # 3d viewer and progress bar
        playback = gui.Vert()
        scene_widget = gui.SceneWidget()
        placeholder = gui.Widget()# add rectangle instead of 3d viewer as placeholder
        placeholder.background_color = (gui.Color(1, 0, 0, 1))
        placeholder.frame.width = 1600
        placeholder.frame.height = 900

        playback.add_child(placeholder)
#       playback.add_child(scene_widget)

        media_controls = gui.Horiz()
        play_pause = gui.Button("play/pause")
        progress_bar = gui.ProgressBar()
        progress_bar.value = 0.4

        media_controls.add_child(play_pause)
        media_controls.add_child(progress_bar)

        playback.add_child(media_controls)

        # init settings panel
        settings = gui.Vert()

        # fps
        fps = gui.Horiz()
        fps_text = gui.Label("FPS:")
        fps_input = gui.TextEdit()

        fps.add_child(fps_text)
        fps.add_child(fps_input)

        # frame step
        frame_step = gui.Vert()
        frame_step_label = gui.Label("Step frames")
        frame_step_buttons = gui.Horiz()
        frame_step_back = gui.Button("Previous")
        frame_step_forward = gui.Button("Next")

        frame_step_buttons.add_child(frame_step_back)
        frame_step_buttons.add_child(frame_step_forward)
        frame_step.add_child(frame_step_label)
        frame_step.add_child(frame_step_buttons)

        # Camera Controls
        camera_placeholder = gui.Widget()
        camera_placeholder.frame.width = 200
        camera_placeholder.frame.height = 400

        # Save button
        save_button = gui.Button("Save")

        # add everything to the panel
        settings.add_child(fps)
        settings.add_child(frame_step)
        settings.add_child(camera_placeholder)
        settings.add_child(save_button)

        frame.add_child(playback)
        frame.add_child(settings)

        interface.add_child(frame)

def main():
    gui.Application.instance.initialize()
    window = Window()
    gui.Application.instance.run()



if __name__ == '__main__':
    main()
