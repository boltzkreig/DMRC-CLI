from time import sleep
from math import hypot, degrees, atan2, radians, cos
from os import environ
import json
import sys
import threading
import subprocess
from hashlib import file_digest
from pathlib import Path
from datetime import datetime, timedelta

import requests
from pyfzf.pyfzf import FzfPrompt
from tcolorpy import tcolor as tc
from assets import frames, Alias

sheet = {"timeCollection": [], "body": []}
session = requests.Session()
Aux_Dir = Path(__file__).parent.parent / "aux"
Aux_Dir.mkdir(exist_ok=True)
ENDPOINT = "https://backend.delhimetrorail.com/api/v2/en"
LINE_FILE = Aux_Dir / "line_index.json"
CACHE_FILE = Aux_Dir / "stations_cache.json"
STATION_FILE = Aux_Dir / "stations_index.json"
PROXIMITY_FILE = Aux_Dir / "station_location.json"
# line_list # facility_category # service_information # station_by_keyword/all/### # station_by_line/LN#
# new_fare_with_route/HDNR/NDI/least-distance/
LAT_DIS = 111.195

session.headers.update(
    {
        "User-Agent": "DMRC CLI",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
)

def run_with_loader(func):
    def loader(signal):
        while not signal.is_set():
            for frame in frames:
                print(f"\r\t{frame}", end="", file=sys.stderr, flush=True)
                if signal.is_set():
                    break
                sleep(0.075)

    def wrapper(*args, **kwargs):
        dummy = {}

        def wrap_func():
            try:
                dummy["res"] = func(*args, **kwargs)
            except:
                print("\r\tFAILURE")

        signal = threading.Event()
        load_thread = threading.Thread(target=loader, args=(signal,))
        load_thread.daemon = True
        acti_thread = threading.Thread(target=wrap_func)
        load_thread.start()
        acti_thread.start()
        acti_thread.join()
        signal.set()
        load_thread.join()
        if environ.get("JSON","False") == "True":
            json.dump(dummy["res"], sys.stderr, indent=4)
        return dummy["res"]

    return wrapper


@run_with_loader
def get_from_sensors(arguments):
    res = json.loads(subprocess.check_output(arguments))
    return res


@run_with_loader
def request_handler(url):
    try:
        res = session.get(url).json()
    except Exception as e:
        print(tc("\r[ERROR] ", color="#ff0000") + str(e) + " Try again.")
        sys.exit()
    return res


def generate_json():
    def get_station_list(station_id):
        res = request_handler(f"{ENDPOINT}/station_by_line/{station_id}")
        return res

    def get_line_list():
        res = request_handler(f"{ENDPOINT}/line_list")
        for line in res:
            print(
                f"\r\t{line['line_code']:<4} {tc('\u2588',color=line['primary_color_code'])} {line['line_color']:<12}"
            )
        print()
        return res

    print(tc("UPDATING LINES & STATIONS LIST\n", styles=["bold"]))
    all_lines = {}
    all_stations = {}
    last_stat_found = 0
    for line in get_line_list():
        all_lines[line["id"]] = line["primary_color_code"]
        for station in get_station_list(line["line_code"]):
            all_stations[station["station_name"]] = station["station_code"]
        print(
            f"\r\t{tc(str(len(all_stations)-last_stat_found),styles=['bold']):<12} Unique Stations Found on {line['line_color']}"
        )
        last_stat_found = len(all_stations)
    with open(STATION_FILE, "w") as file:
        json.dump(dict(sorted(all_stations.items())), file, indent=0)
    with open(LINE_FILE, "w") as file:
        json.dump(dict(sorted(all_lines.items())), file, indent=0)


def read_json(name):
    try:
        _hash = file_digest(open(name, "rb"), "sha3_512").hexdigest()
        if datetime.now().timestamp() - name.stat().st_mtime > (60 * 60 * 24 * 7):
            if input(f"{name.name} is stale. Wish to refresh?(y/N) ") == "y":
                raise LookupError("Stale Files")
    except Exception as e:
        print(
            tc("[ERROR] ", color="#ff0000") + str(e) + " Trying to Generate Cache Files"
        )
        generate_json()
        Path(CACHE_FILE).touch(exist_ok=True)
    finally:
        with open(name, "r") as file:
            return json.load(file)
        if _hash == file_digest(open(name, "rb"), "sha3_512").hexdigest():
            print("Found  Nothing New in", name)
        else:
            print("Found Something New in", name)


def poll_station(extra):
    fzf = FzfPrompt()
    selection = fzf.prompt(stations.keys(), extra)
    if not selection:
        mesg = f"{extra[9:]}." if extra[0:8] == "--filter" else ""
        print("\r" + tc("[INFO] ", color="#ffff00") + mesg + " No Selection Made")
        sys.exit()
    return stations[selection[0]]


def symbolise(raw_token):
    token = raw_token.split('&')[0].strip(' ').lower()
    if token.endswith('s'): token = token[:-1]
    return Alias.get(token, raw_token)

def setup_vars(FROM, VIA, DEST, ALGO, RETRY):
    try:
        if RETRY:
            with open(CACHE_FILE, "r") as file:
                _FROM, _VIA, _DEST = json.load(file)
        if RETRY == 2:
            _FROM, _DEST = _DEST, _FROM
    except:
        _FROM, _VIA, _DEST = [None, None, None]

    finally:
        if FROM is None:
            if RETRY:
                FROM = _FROM
            else:
                FROM = poll_station("--prompt='FROM: '")
        else:
            FROM = poll_station(f'--filter="{FROM}"')

        if VIA is not False:
            if VIA is None:
                if RETRY:
                    VIA = _VIA
                else:
                    VIA = poll_station("--prompt='VIA: '")
            else:
                VIA = poll_station(f'--filter="{VIA}"')

        if DEST is None:
            if RETRY:
                DEST = _DEST
            else:
                DEST = poll_station("--prompt='DEST: '")
        else:
            DEST = poll_station(f'--filter="{DEST}"')

        ALGO = "minimum-interchange" if ALGO == "MI" else "least-distance"
        return [ FROM, VIA, DEST, ALGO ]


stations = read_json(STATION_FILE)
lines = read_json(LINE_FILE)
