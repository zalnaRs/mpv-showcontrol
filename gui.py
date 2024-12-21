import dearpygui.dearpygui as dpg
import threading
from main import read_playlist_config, ShowControl, save_playlist_config, move_playlist_item_up, move_playlist_item_down

class App:
    def __init__(self):
        self.control = None
        self.playlist = []
        self.current_index = -1
        self.selected_index = 0
        self.current_label = "Current: None"
        self.selected_label = "Selected: None"
        self.config_file = None

    def load_config(self, sender, app_data):
        self.config_file = app_data['file_path_name']
        config = read_playlist_config(self.config_file)
        if config:
            self.control = ShowControl(config, self.update_current_label)
            self.control.load_playlist()
            self.playlist = self.control.playlist
            self.update_current_label(0)
            self.populate_playlist_table()
        else:
            print("Failed to read configuration file")

    def update_current_label(self, index):
        self.current_label = f"Current: {self.control.format_playlist_item(index)}" if index < len(self.playlist) else "Current: None"
        dpg.set_value("current_label", self.current_label)

    def update_selected_label(self, index):
        self.selected_label = f"Selected: {self.control.format_playlist_item(index)}" if index < len(self.playlist) else "Selected: None"
        dpg.set_value("selected_label", self.selected_label)

    def play_selected(self):
        if self.control and self.selected_index >= 0:
            self.current_index = self.selected_index
            self.play()

    def play(self):
        if self.control and self.current_index >= 0:
            threading.Thread(target=self.control.play, args=(self.current_index,)).start()

    def next(self):
        if self.control:
            threading.Thread(target=self.control.skip_to_next).start()
            self.update_current_label(self.control.current_index)

    def previous(self):
        if self.control:
            threading.Thread(target=self.control.skip_to_previous).start()
            self.update_current_label(self.control.current_index)

    def select_playlist_item(self, sender, app_data, user_data):
        self.selected_index = user_data
        self.update_selected_label(user_data)

    def add_playlist_item(self, sender, app_data):
        new_item = {
            'file': dpg.get_value("file_input"),
            'volume': int(dpg.get_value("volume_input")),
            'loop': dpg.get_value("loop_input"),
            'start-time': dpg.get_value("start_time_input"),
            'skip-time': dpg.get_value("skip_time_input")
        }
        self.playlist.append(new_item)
        self.populate_playlist_table()

    def edit_playlist_item(self, sender, app_data):
        if self.selected_index >= 0:
            self.playlist[self.selected_index] = {
                'file': dpg.get_value("file_input"),
                'volume': int(dpg.get_value("volume_input")),
                'loop': dpg.get_value("loop_input"),
                'start-time': dpg.get_value("start_time_input"),
                'skip-time': dpg.get_value("skip_time_input")
            }
            self.populate_playlist_table()

    def remove_playlist_item(self, sender, app_data):
        if self.selected_index >= 0:
            del self.playlist[self.selected_index]
            self.selected_index = -1
            self.populate_playlist_table()

    def populate_playlist_table(self):
        dpg.delete_item("playlist_table", children_only=True)
        columns = ["Index", "File", "Volume", "Loop", "Start Time", "Skip Time", "Action"]
        for col in columns:
            dpg.add_table_column(parent="playlist_table", label=col, width_stretch=True)
        for i, item in enumerate(self.playlist):
            with dpg.table_row(parent="playlist_table", tag=f"row_{i}"):
                dpg.add_text(str(i+1))
                dpg.add_text(item['file'])
                dpg.add_text(str(item.get('volume', 100)))
                dpg.add_text("Yes" if item.get('loop') else "No")
                dpg.add_text(item.get('start-time', "00:00:00"))
                dpg.add_text(item.get('skip-time', "end_file"))
                dpg.add_button(label="Select", callback=self.select_playlist_item, user_data=i)

    def save_playlist(self, sender, app_data):
        dpg.show_item("save_file_dialog_id")

    def save_playlist_to_file(self, sender, app_data):
        file_path = app_data['file_path_name']
        if file_path:
            save_playlist_config(file_path, self.playlist)
            print(f"Playlist saved to {file_path}")
        else:
            print("No file path provided")

    def move_playlist_item_up_gui(self, sender, app_data):
        if self.selected_index >= 0:
            move_playlist_item_up(self, self.selected_index)
            self.selected_index = max(0, self.selected_index - 1)
            self.populate_playlist_table()

    def move_playlist_item_down_gui(self, sender, app_data):
        if self.selected_index >= 0:
            move_playlist_item_down(self, self.selected_index)
            self.selected_index = min(len(self.playlist) - 1, self.selected_index + 1)
            self.populate_playlist_table()

    def run(self):
        dpg.create_context()

        with dpg.font_registry():
            default_font = dpg.add_font("inter.ttf", 20)

        with dpg.window(tag="main_window", label="Controls", width=640, height=720, pos=[0, 0]):
            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="Open", callback=lambda: dpg.show_item("file_dialog_id"))
                    dpg.add_menu_item(label="Save", callback=self.save_playlist)
                    dpg.add_menu_item(label="Exit", callback=dpg.stop_dearpygui)
                with dpg.menu(label="Edit"):
                    dpg.add_menu_item(label="Edit Playlist", callback=lambda: dpg.show_item("edit_window"))
            dpg.add_text(self.current_label, tag="current_label")
            dpg.add_button(label="Next", callback=self.next)
            dpg.add_button(label="Previous", callback=self.previous)

        with dpg.window(tag="playlist_window", label="Playlist", width=640, height=720, pos=[640, 0]):
            with dpg.menu_bar():
                dpg.add_button(label="Play Selected", callback=self.play_selected)
                dpg.add_text(self.selected_label, tag="selected_label")
            with dpg.table(tag="playlist_table", header_row=True):
                dpg.add_table_column(label="No playlist", width_stretch=True)

        with dpg.window(tag="edit_window", label="Edit Playlist", width=640, height=340, show=False):
            dpg.add_input_text(label="File", tag="file_input")
            dpg.add_input_int(label="Volume", tag="volume_input", default_value=100)
            dpg.add_checkbox(label="Loop", tag="loop_input")
            dpg.add_input_text(label="Start Time", tag="start_time_input", default_value="00:00:00")
            dpg.add_input_text(label="Skip Time", tag="skip_time_input", default_value="end_file")
            dpg.add_button(label="Add", callback=self.add_playlist_item)
            dpg.add_button(label="Edit", callback=self.edit_playlist_item)
            dpg.add_button(label="Remove", callback=self.remove_playlist_item)
            dpg.add_button(label="Move Up", callback=self.move_playlist_item_up_gui)
            dpg.add_button(label="Move Down", callback=self.move_playlist_item_down_gui)

        with dpg.file_dialog(directory_selector=False, show=False, callback=self.load_config, id="file_dialog_id"):
            dpg.add_file_extension(".json")
        with dpg.file_dialog(directory_selector=False, show=False, callback=self.save_playlist_to_file, id="save_file_dialog_id", width=400, height=300):
            dpg.add_file_extension(".json")

        dpg.bind_font(default_font)
        dpg.create_viewport(title='MPV Show Control', width=1280, height=720)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

if __name__ == "__main__":
    app = App()
    app.run()