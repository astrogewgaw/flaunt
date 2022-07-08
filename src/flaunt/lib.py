import os
import json

from pathlib import Path
from fontTools import ttLib
from os import environ as ENV
from datetime import datetime as dt
from subprocess import check_output

ISO = "%Y-%m-%dT%H:%M:%S"
Config = Path.home() / ".flaunt.json"
X11Home = Path(ENV.get("XDG_DATA_HOME", ""))

X11FontDirs = [
    "/usr/share/fonts/",
    "/usr/X11/lib/X11/fonts",
    "/usr/local/share/fonts/",
    f"{Path.home() / '.fonts'}",
    "/usr/X11R6/lib/X11/fonts/TTF/",
    "/usr/lib/openoffice/share/fonts/truetype/",
    f"{X11Home or Path.home() / '.local/share'}",
]

ext_aliases = lambda ext: {
    "afm": ["afm"],
    "otf": ["otf", "ttc", "ttf"],
    "ttc": ["otf", "ttc", "ttf"],
    "ttf": ["otf", "ttc", "ttf"],
}[ext]

fclist = lambda: [
    Path(os.fsdecode(fname))
    for fname in check_output(
        [
            "fc-list",
            "--format=%{file}\\n",
        ]
    ).split(b"\n")
]


def fontpaths(ext="ttf"):
    return [
        _
        for _ in [
            Path(font)
            for font in fclist()
            if font.suffix.lower()[1:] in ext_aliases(ext=ext)
        ]
        if _.exists()
    ]


def fontlist():
    if Config.exists():
        with open(Config, "r") as fp:
            data = json.load(fp=fp)
            if (dt.now() - dt.strptime(data["updated"], ISO)).days < 7:
                return data["names"]

    names = []
    for ext in ["afm", "ttf"]:
        for path in fontpaths(ext=ext):
            if path.suffix.lower()[1:] == "ttc":
                for font in ttLib.TTCollection(path):
                    names.append(font["name"].getDebugName(1))
            else:
                names.append(ttLib.TTFont(str(path))["name"].getDebugName(1))  # type: ignore
    with open(Config, "w+") as fp:
        json.dump(
            fp=fp,
            indent=4,
            obj={
                "names": sorted(list(set(names))),
                "updated": f"{dt.now().strftime(ISO)}",
            },
        )
    return names


def get_nerd_font():
    pass


def get_google_font():
    pass


def update_font_cache():
    pass
