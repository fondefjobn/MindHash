import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering


class ExampleWindow:

    def __init__(self):
        interface = gui.Application.instance.create_window("Mindhash", 1920, 1080)

        frame = gui.Horiz()

        # 3d viewer and progress bar
        playback = gui.Vert()
        scene_widget = gui.SceneWidget()
        scene_widget.frame.width = 1600
        scene_widget.frame.height = 900
        scene = rendering.Open3DScene(interface.renderer)
        scene_widget.scene = scene

        bbox = o3d.geometry.AxisAlignedBoundingBox([-10, -10, -10],
                                                   [10, 10, 10])

        scene_widget.setup_camera(60, bbox, [0, 0, 0])
        scene.set_background([0, 0, 0, 1])
        cone = o3d.geometry.TriangleMesh.create_cone()
        material = rendering.Material()
        scene.add_geometry("cone", cone, material)

        playback.add_child(scene_widget)

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
        camera_area = gui.Vert()

        camera_placeholder = gui.Button("")  # empty button for spacing, better solution should be found
        camera_placeholder.visible = False
        camera_rotate_left = gui.Button("")
        camera_move_left = gui.Button("")
        camera_rotate_up = gui.Button("")
        camera_move_up = gui.Button("")
        camera_zoom = gui.Vert()
        camera_zoom_in = gui.Button("")
        camera_zoom_out = gui.Button("")
        camera_zoom.add_child(camera_zoom_in)
        camera_zoom.add_child(camera_zoom_out)

        camera_move_down = gui.Button("")
        camera_rotate_down = gui.Button("")
        camera_move_right = gui.Button("")
        camera_rotate_right = gui.Button("")

        grid = [
            [None, None, camera_rotate_up, None, None],
            [None, None, camera_move_up, None, None],
            [camera_rotate_left, camera_move_left, camera_zoom, camera_move_right, camera_rotate_right],
            [None, None, camera_move_down, None, None],
            [None, None, camera_rotate_down, None, None],
        ]
        camera_control = gui.VGrid(len(grid[0]), spacing=1)

        for row in grid:
            for element in row:
                if element:
                    camera_control.add_child(element)
                else:
                    camera_control.add_child(camera_placeholder)

        camera_third_person = gui.Button("Third person")
        camera_top_down = gui.Button("Top down")

        camera_area.add_child(camera_control)
        camera_area.add_child(camera_third_person)
        camera_area.add_child(camera_top_down)

        # Save button
        save_button = gui.Button("Save")

        # add everything to the panel
        settings.add_child(fps)
        settings.add_child(frame_step)
        settings.add_child(camera_area)
        settings.add_child(save_button)

        frame.add_child(playback)
        frame.add_child(settings)

        interface.add_child(frame)


def main():
    gui.Application.instance.initialize()
    window = ExampleWindow()
    gui.Application.instance.run()


if __name__ == '__main__':
    main()
