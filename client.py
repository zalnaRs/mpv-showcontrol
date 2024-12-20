import json

import mpv

class Client:
    def __init__(self, ipc_path, start_mpv, mpv_path):
        self.mpv = mpv.MPV(
            input_default_bindings=True,
            input_vo_keyboard=True,
            osc=True
        )

    def play(self, file):
        # parse the output json
        # {"request_id":0,"error":"success"}
        # if error is not success, print error
        self.mpv.play(file)
        self.mpv.wait_until_playing()

    def seek(self, time):
        self.mpv.seek(time)

    def get_volume(self):
        return self.mpv.volume

    def set_volume(self, volume):
        self.mpv.volume = volume

    def set_loop(self, loop):
        self.mpv.loop = loop

    def close(self):
        self.mpv.quit(0)

    def get_time(self):
        return self.mpv.time_pos

    def get_duration(self):
        return self.mpv.duration

    def wait_for_end(self):
        self.mpv.wait_for_playback(timeout=self.get_duration()-self.get_time())
        return True