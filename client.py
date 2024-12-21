import time
import mpv

from util import parse_time


class Client:
    def __init__(self):
        self.mpv = mpv.MPV(
            input_default_bindings=True,
            input_vo_keyboard=True,
            osc=True
        )
        self.time_pos = 0

        @self.mpv.property_observer('time-pos')
        def time_observer(_name, value):
            #print('Now playing at {:.2f}s'.format(value))
            if value:
                self.time_pos = value
            else:
                self.time_pos = 0


    def play(self, file):
        self.mpv.play(file)
        self.mpv.wait_until_playing()

    def seek(self, time):
        self.mpv.seek(time)

    def set_volume(self, volume):
        self.mpv.volume = volume

    def set_loop(self, loop):
        self.mpv.loop = loop

    def wait_for_end(self):
        try:
            if not self.mpv.duration is None:
                self.mpv.wait_until_playing()
                time.sleep(0.1)
                self.mpv.wait_for_event("end_file")
                return True
        except Exception as e:
            print(f"Failed to wait for end: {e}")
            return False

    def wait_for_time(self, start_time, skip_time):
        try:
            self.mpv.wait_until_playing()
            time.sleep(0.1)
            skip_time = parse_time(start_time) + parse_time(skip_time)
            while not float(self.time_pos) >= skip_time:
                time.sleep(0.1)  # Add sleep interval to prevent high CPU usage
            return True
        except Exception as e:
            print(f"Failed to wait for time: {e}")
            return False
