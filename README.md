# MPV Show Control

<div>
<img alt="Made with Python" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img alt="Github repo stars" src="https://img.shields.io/github/stars/zalnaRs/mpv-showcontrol?style=for-the-badge" />
</div>

A simple show control written in Python using python-mpv (libmpv) and a GUI using Dear PyGui.

## Development/Building

### Requirements

- Python 3.13 (others could work)
- All of the dependencies in `requirements.txt`, install with: `pip install -r requirements.txt # or pip3`
- [mpv](https://mpv.io/), preferably in `PATH`

### Running

To run the GUI:
```bash
python3 ./gui.py # or python, py
```

If you only want the CLI:
```bash
python3 ./main.py # or python, py
```

## Usage

### Configuration
You can create the config file either, with the GUI or manually.
The syntax of a `*.json` config file is like so:
```json
{
    "playlist": [
        {
            "file": "./intermission.mkv",
            "loop": true
        },
        {
            "file": "./a.mp4",
            "volume": 50,
            "start-time": "00:01:00",
            "skip-time": "00:00:05"
        },
        {
            "file": "./a.mp4",
            "volume": 50,
            "start-time": "00:08:55"
        },
        {
            "file": "./b.mp4"
        },
        {
            "file": "./a.mp4",
            "volume": 25,
            "loop": true,
            "start-time": "00:08:53",
            "skip-time": "end_file"
        }
    ]
}
```

---

You should have a black/logo/intermission video looping, so you can setup screen layout, window placement etc...
