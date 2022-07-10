import os
import json
import shutil
import zipfile
import tempfile
import requests

from pathlib import Path
from github import Github
from subprocess import run
from appdirs import AppDirs
from fontTools import ttLib
from os import environ as ENV
from datetime import datetime as dt
from subprocess import check_output

g = Github()

AppName = "flaunt"
Author = "Ujjwal Panda"
ISO = "%Y-%m-%dT%H:%M:%S"
Dirs = AppDirs(AppName, Author)
X11Home = Path(ENV.get("XDG_DATA_HOME", ""))
Config = Path(Dirs.user_config_dir) / f"{AppName}.json"
NFDB = Path(Dirs.user_data_dir) / f"{AppName}_nfdb.json"

X11FontDirs = [
    "/usr/share/fonts/",
    "/usr/X11/lib/X11/fonts",
    "/usr/local/share/fonts/",
    f"{Path.home() / '.fonts'}",
    "/usr/X11R6/lib/X11/fonts/TTF/",
    "/usr/lib/openoffice/share/fonts/truetype/",
    f"{(X11Home or Path.home()) / '.local/share/fonts'}",
]

UsrFontDir = (X11Home or Path.home()) / ".local/share/fonts"

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

flatten = lambda x: [_ for __ in x for _ in __]


def make_appdirs():
    CD = Path(Dirs.user_data_dir)
    DD = Path(Dirs.user_config_dir)

    if not CD.exists():
        CD.mkdir()

    if not DD.exists():
        DD.mkdir()


def remove_appdirs():
    CD = Path(Dirs.user_data_dir)
    DD = Path(Dirs.user_config_dir)

    if CD.exists():
        shutil.rmtree(CD)

    if DD.exists():
        shutil.rmtree(DD)


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

    names = sorted(list(set(names)))

    with open(Config, "w+") as fp:
        json.dump(
            fp=fp,
            indent=4,
            obj={
                "names": names,
                "updated": f"{dt.now().strftime(ISO)}",
            },
        )

    return names


def get_nerd_font(font):
    version = nerd_font_list()["version"]
    response = requests.get(
        "/".join(
            [
                "https://github.com",
                "ryanoasis",
                "nerd-fonts",
                "releases",
                "download",
                version,
                f"{font}.zip",
            ]
        )
    )

    if response.status_code == requests.codes.ok:
        with tempfile.NamedTemporaryFile(suffix="zip") as f:
            f.write(response.content)
            with zipfile.ZipFile(f.name) as zipped:
                zipped.extractall(path=UsrFontDir)
        update_font_cache()


def nerd_font_list():
    if NFDB.exists():
        with open(NFDB, "r") as fp:
            fonts = json.load(fp=fp)
            if (dt.now() - dt.strptime(fonts["updated"], ISO)).days < 7:
                return fonts

    repo = g.get_repo("ryanoasis/nerd-fonts")
    release = repo.get_latest_release()
    version = release.title

    names = [
        _.name.replace(".zip", "")
        for _ in flatten(
            [
                [_ for _ in release.get_assets().get_page(i)]
                for i in range(-(-release.get_assets().totalCount // 25))
            ]
        )
    ]

    fonts = {
        "version": version,
        "names": list(set(names)),
        "updated": f"{dt.now().strftime(ISO)}",
    }

    with open(NFDB, "w+") as fp:
        json.dump(
            fp=fp,
            indent=4,
            obj=fonts,
        )

    return fonts


def update_font_cache():
    process = run(["fc-cache", "-fv"])
    return process.returncode
