import json
import time

import client

def read_playlist_config(config_file):
    """Reads the configuration from a JSON file.

    Args:
      config_file: Path to the JSON configuration file.

    Returns:
      A dictionary representing the parsed JSON data, or None if an error occurs.
    """
    """
    {
  "playlist": [
    {"file": "./intermission.mkv", "loop": true},
    {"file": "./a.mp4", "volume": 50, "start-time": "00:01:00", "skip-time": "00:00:30"},
    {"file": "./b.mp4"},
    {"file": "./intermission.mkv", "loop": true}
  ],
  "start-mpv": true,
  "ipc-path": "/tmp/mpv-socket",
  "mpv-location": "/usr/bin/mpv"
}

"""
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)

        if 'playlist' not in config_data:
            print("Error: 'playlist' key is missing in configuration")
            return None
        if not isinstance(config_data['playlist'], list):
            print("Error: 'playlist' key must be a list")
            return None
        for item in config_data['playlist']:
            if 'file' not in item:
                print("Error: 'file' key is missing in playlist item")
                return None
            if 'loop' in item and not isinstance(item['loop'], bool):
                print("Error: 'loop' key must be a boolean")
                return None
            if 'volume' in item and not isinstance(item['volume'], int):
                print("Error: 'volume' key must be an integer")
                return None
            if 'start-time' in item and not isinstance(item['start-time'], str):
                print("Error: 'start-time' key must be a string")
                return None
            if 'skip-time' in item and not isinstance(item['skip-time'], str):
                print("Error: 'skip-time' key must be a string")
                return None
        if not 'ipc-path' in config_data and 'start-mpv' in config_data and not isinstance(config_data['start-mpv'], bool):
            print("Error: 'start-mpv' key must be a boolean")
            return None
        if not 'start-mpv' in config_data and 'ipc-path' in config_data and not isinstance(config_data['ipc-path'], str):
            print("Error: 'ipc-path' key must be a string")
            return None
        if not 'mpv-location' in config_data and not isinstance(config_data['mpv-location'], str):
            print("Error: 'mpv-location' key must be a string")
            return None

        return config_data
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_file}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {config_file}")
        return None

def format_playlist_item(item, minimal = False):
    """Formats a playlist item for display.

    Args:
      item: A dictionary representing a playlist item.

    Returns:
      A string containing the formatted playlist item.
      :param minimal:
    """
    """
    {
  "file": "./intermission.mkv",
  "loop": true
}
    """
    if minimal:
        return item['file']
    else:
        formatted_item = f"File: {item['file']}"
        if 'volume' in item:
            formatted_item += f", Volume: {item['volume']}"
        if 'start-time' in item:
            formatted_item += f", Start time: {item['start-time']}"
        if 'skip-time' in item:
            formatted_item += f", Skip time: {item['skip-time']}"
        if 'loop' in item and item['loop']:
            formatted_item += ", Looping"
        return formatted_item


def quit():
    exit(0)

class ShowControl:
    def __init__(self, config):
        self.config = config
        self.playlist = []
        self.current_index = 0
        self.commands = [
            ({'name':'next', 'description': 'Play the next item in the playlist', 'callback': self.skip_to_next}),
            ({'name':'previous', 'description': 'Play the previous item in the playlist', 'callback': self.skip_to_previous}),
            ({'name':'play <index>', 'description': 'Play the item at the specified index in the playlist', 'callback': self.play}),
            ({'name':'playlist', 'description': 'Show the playlist', 'callback': self.show_playlist}),
            ({'name':'current', 'description': 'Show the current item in the playlist', 'callback': self.show_current}),
            ({'name':'help', 'description': 'Show this help message', 'callback': self.show_help}),
            ({'name':'exit', 'description': 'Exit the program', 'callback': quit})
        ]
        self.client = client.Client(config['ipc-path'], config['start-mpv'], config['mpv-location'])


    def load_playlist(self):
        self.playlist = self.config['playlist']
        print(f"Loaded playlist with {len(self.playlist)} items")

    def play(self, index):
        if index < len(self.playlist):
            self.current_index = index
            playlist_item = self.playlist[self.current_index]

            self.client.play(playlist_item['file'])
            self.client.set_volume(playlist_item['volume'] if 'volume' in playlist_item else 100)
            self.client.set_loop(playlist_item['loop'] if 'loop' in playlist_item else False)
            if 'start-time' in playlist_item:
                self.client.seek(playlist_item['start-time'])

            print(f"Playing {self.playlist[self.current_index]}")

            # if self.current_index < len(self.playlist) - 1:
            #     print(f"Next up: {format_playlist_item(self.playlist[self.current_index+1], minimal = True)}")

            # if skip-time is defined wait for that amount of time before skipping to the next item
            if 'skip-time' in playlist_item:
                # parse the time in HH:MM:SS format
                time_parts = playlist_item['skip-time'].split(':')
                skip_time = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
                time.sleep(skip_time)
                self.skip_to_next()
            elif not 'loop' in playlist_item or not playlist_item['loop']:
                if self.client.wait_for_end():
                    self.skip_to_next()

        else:
            print("Invalid playlist index")

    def skip_to_next(self):
        if self.current_index < len(self.playlist):
            self.current_index += 1
            self.play(self.current_index)
        else:
            print("End of playlist reached")

    def skip_to_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.play(self.current_index)
        else:
            print("Beginning of playlist reached")

    def show_playlist(self):
        print("Playlist:")
        for i, item in enumerate(self.playlist):
            print(f"{i+1}. {format_playlist_item(item)}")

    def show_current(self, minimal = False):
        if minimal:
            print(format_playlist_item(self.playlist[self.current_index]))
        else:
            print(f"Current index: {self.current_index+1}/{len(self.playlist)}")
            print(f"Current item: ")
            print(format_playlist_item(self.playlist[self.current_index]))
            print(f"Next item: {format_playlist_item(self.playlist[self.current_index+1], True)}")
            print(f"Previous item: {format_playlist_item(self.playlist[self.current_index-1], True)}")

    def show_help(self):
        print("Commands:")
        for command in self.commands:
            print(f"{command['name']}: {command['description']}")

    def show_menu(self):
        while True:
            print("--------------------")
            # self.show_help()
            # print("--------------------")
            self.show_current(minimal = True)
            print("--------------------")
            command = input("> ")
            print("--------------------")
            parts = command.split()
            if len(parts) == 0:
                continue

            for command in self.commands:
                if parts[0] == command['name']:
                    if len(parts) == 1:
                        command['callback']()
                    else:
                        try:
                            index = int(parts[1])
                            command['callback'](index)
                            break
                        except ValueError:
                            print("Invalid index")
                    break

    def run(self):
        self.load_playlist()
        time.sleep(1)
        self.play(0)
        self.show_menu()


if __name__ == "__main__":
    config = read_playlist_config('config.json')
    if config:
        control = ShowControl(config)
        control.run()
    else:
        print("Error: Failed to read configuration file")
        exit(1)